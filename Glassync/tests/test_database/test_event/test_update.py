from django.test import TestCase
from Glassync.models import Event, User
from Glassync.database.event.services import create_or_update_event


class TestUpdateEvent(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a test user without a username
        self.creator = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )

        self.other_user = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )

        # Create an event to update
        self.event = Event.objects.create(
            name="Original Event",
            description="Original description",
            date="2025-05-15",
            time_start="10:00:00",
            time_end="11:00:00",
            recurrence_rule_type="daily",
            recurrence_rule_interval=1,
            creator=self.creator
        )

    def test_successful_update(self):
        """Test updating an event successfully."""
        result = create_or_update_event(
            event_id=self.event.id,
            name="Updated Event",
            description="Updated description",
            date="2025-05-16",
            time_start="12:00:00",
            time_end="13:00:00",
            recurrence_rule_type="weekly",
            recurrence_rule_interval=2,
            user_id=self.creator.id
        )

        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 200)
        self.assertIsInstance(result['event'], Event)

        # Verify the database reflects the updates
        updated_event = Event.objects.get(id=self.event.id)
        self.assertEqual(updated_event.name, "Updated Event")
        self.assertEqual(updated_event.description, "Updated description")
        self.assertEqual(str(updated_event.date), "2025-05-16")
        self.assertEqual(str(updated_event.time_start), "12:00:00")
        self.assertEqual(str(updated_event.time_end), "13:00:00")
        self.assertEqual(updated_event.recurrence_rule_type, "weekly")
        self.assertEqual(updated_event.recurrence_rule_interval, 2)

    def test_permission_denied(self):
        """Test updating an event by a non-creator results in a permission error."""
        result = create_or_update_event(
            event_id=self.event.id,
            name="Attempted Update",
            user_id=self.other_user.id
        )

        self.assertIn('error', result)
        self.assertEqual(result['status'], 403)
        self.assertEqual(result['error'], 'Permission denied. Only the creator can edit this event.')

    def test_event_not_found(self):
        """Test updating a non-existent event results in an error."""
        result = create_or_update_event(
            event_id=9999,  # Non-existent event ID
            name="Non-Existent Event",
            user_id=self.creator.id
        )

        self.assertIn('error', result)
        self.assertEqual(result['status'], 404)
        self.assertEqual(result['error'], 'Event with ID 9999 does not exist')

    def test_invalid_time_range(self):
        """Test updating an event with invalid time range results in a validation error."""
        result = create_or_update_event(
            event_id=self.event.id,
            time_start="14:00:00",
            time_end="13:00:00",  # Invalid time range
            user_id=self.creator.id
        )

        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'time_start must be earlier than time_end')

    def test_invalid_recurrence_rule_type(self):
        """Test updating an event with an invalid recurrence rule type."""
        result = create_or_update_event(
            event_id=self.event.id,
            recurrence_rule_type="infinity",  # Invalid type
            user_id=self.creator.id
        )

        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Invalid recurrence_rule_type. Must be one of [\'daily\', \'weekly\', \'monthly\', \'yearly\']')

    def test_invalid_date_format(self):
        """Test updating an event with an invalid date format."""
        result = create_or_update_event(
            event_id=self.event.id,
            date="15-05-2025",  # Invalid date format
            user_id=self.creator.id
        )

        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Invalid date format. Use YYYY-MM-DD')

    def test_no_changes(self):
        """Test updating an event without making any changes."""
        result = create_or_update_event(
            event_id=self.event.id,
            user_id=self.creator.id
        )

        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 200)

        # Verify that no changes occurred
        updated_event = Event.objects.get(id=self.event.id)
        self.assertEqual(updated_event.name, "Original Event")
        self.assertEqual(updated_event.description, "Original description")
        self.assertEqual(str(updated_event.date), "2025-05-15")
        self.assertEqual(str(updated_event.time_start), "10:00:00")
        self.assertEqual(str(updated_event.time_end), "11:00:00")
        self.assertEqual(updated_event.recurrence_rule_type, "daily")
        self.assertEqual(updated_event.recurrence_rule_interval, 1)