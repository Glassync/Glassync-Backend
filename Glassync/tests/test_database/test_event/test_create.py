from django.test import TestCase
from Glassync.models import Event, User
from Glassync.database.event.services import create_or_update_event


class Tests(TestCase):
    def setUp(self):
        # Create a test user
        self.creator = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )

    def test_valid_event_creation(self):
        """Test creating an event with valid data and verifying it exists in the database."""
        # Call the function to create the event
        result = create_or_update_event(
            name="Test Event",
            description="A valid test event",
            date="2025-05-15",
            time_start="10:00:00",
            time_end="11:00:00",
            recurrence_rule_type="daily",
            recurrence_rule_interval=1,
            creator=self.creator
        )

        # Assert no errors in the result
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 201)
        self.assertIsInstance(result['event'], Event)

        # Verify the event exists in the database
        created_event = Event.objects.get(id=result['event'].id)
        self.assertEqual(created_event.name, "Test Event")
        self.assertEqual(created_event.description, "A valid test event")
        self.assertEqual(str(created_event.date), "2025-05-15")
        self.assertEqual(str(created_event.time_start), "10:00:00")
        self.assertEqual(str(created_event.time_end), "11:00:00")
        self.assertEqual(created_event.recurrence_rule_type, "daily")
        self.assertEqual(created_event.recurrence_rule_interval, 1)
        self.assertEqual(created_event.creator, self.creator)

    def test_missing_required_fields(self):
        """Test creating an event with missing required fields."""
        result = create_or_update_event(
            name="",  # Missing name
            description="Missing required fields",
            date="",
            time_start=None,
            time_end=None,
            recurrence_rule_type=None,
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Missing required fields: name or date')

    def test_invalid_time_format(self):
        """Test creating an event with invalid time format."""
        result = create_or_update_event(
            name="Test Event",
            description="Invalid time format",
            date="2025-05-15",
            time_start="invalid_time",
            time_end="11:00:00",
            recurrence_rule_type=None,
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Invalid time format. Use HH:MM:SS')

    def test_time_start_after_time_end(self):
        """Test creating an event where time_start is after time_end."""
        result = create_or_update_event(
            name="Test Event",
            description="time_start after time_end",
            date="2025-05-15",
            time_start="12:00:00",
            time_end="10:00:00",
            recurrence_rule_type=None,
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'time_start must be earlier than time_end')

    def test_invalid_recurrence_rule_type(self):
        """Test creating an event with an invalid recurrence_rule_type."""
        result = create_or_update_event(
            name="Test Event",
            description="Invalid recurrence_rule_type",
            date="2025-05-15",
            time_start=None,
            time_end=None,
            recurrence_rule_type="invalid_rule",
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Invalid recurrence_rule_type. Must be one of [\'daily\', \'weekly\', \'monthly\', \'yearly\']')

    def test_invalid_recurrence_rule_interval(self):
        """Test creating an event with an invalid recurrence_rule_interval."""
        result = create_or_update_event(
            name="Test Event",
            description="Invalid recurrence_rule_interval",
            date="2025-05-15",
            time_start=None,
            time_end=None,
            recurrence_rule_type="daily",
            recurrence_rule_interval="invalid_interval",  # Not an integer
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'recurrence_rule_interval must be a valid integer')

    def test_negative_recurrence_rule_interval(self):
        """Test creating an event with a negative recurrence_rule_interval."""
        result = create_or_update_event(
            name="Test Event",
            description="Negative recurrence_rule_interval",
            date="2025-05-15",
            time_start=None,
            time_end=None,
            recurrence_rule_type="daily",
            recurrence_rule_interval=-1,  # Negative value
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'recurrence_rule_interval must be a positive integer and less than or equal to 1000')

    def test_large_recurrence_rule_interval(self):
        """Test creating an event with an excessively large recurrence_rule_interval."""
        result = create_or_update_event(
            name="Test Event",
            description="Excessively large recurrence_rule_interval",
            date="2025-05-15",
            time_start=None,
            time_end=None,
            recurrence_rule_type="daily",
            recurrence_rule_interval=1001,  # Greater than 1000
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'recurrence_rule_interval must be a positive integer and less than or equal to 1000')

    def test_invalid_date_format(self):
        """Test creating an event with an invalid date format."""
        result = create_or_update_event(
            name="Test Event",
            description="Invalid date format",
            date="15-05-2025",  # Invalid format
            time_start=None,
            time_end=None,
            recurrence_rule_type=None,
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertIn('error', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Invalid date format. Use YYYY-MM-DD')

    def test_event_creation_without_optional_fields(self):
        """Test creating an event without optional fields."""
        result = create_or_update_event(
            name="Test Event",
            description="No optional fields",
            date="2025-05-15",
            time_start=None,
            time_end=None,
            recurrence_rule_type=None,
            recurrence_rule_interval=None,
            creator=self.creator
        )
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 201)
        self.assertIsInstance(result['event'], Event)