from django.test import TestCase
from Glassync.models import Event, User
from Glassync.database.event.services import get_event_by_uids, can_view_event
from unittest.mock import patch


class TestGetEventByUids(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com"
        )
        self.user2 = User.objects.create(
            first_name="Bob",
            last_name="Johnson",
            email="bob@example.com"
        )

        # Create test events
        self.event1 = Event.objects.create(
            id=101,
            name="Event Created by Alice",
            description="This is Alice's event.",
            date="2025-05-15",
            time_start="10:00:00",
            time_end="12:00:00",
            recurrence_rule_type="daily",
            recurrence_rule_interval=1,
            creator=self.user1
        )
        self.event2 = Event.objects.create(
            id=102,
            name="Event Created by Bob",
            description="This is Bob's event.",
            date="2025-05-16",
            time_start="14:00:00",
            time_end="16:00:00",
            recurrence_rule_type="weekly",
            recurrence_rule_interval=2,
            creator=self.user2
        )
        self.event3 = Event.objects.create(
            id=103,
            name="Event Created by Alice",
            description="Another event by Alice",
            date="2025-05-17",
            time_start="09:00:00",
            time_end="11:00:00",
            recurrence_rule_type="monthly",
            recurrence_rule_interval=1,
            creator=self.user1
        )

    @patch("Glassync.database.event.services.can_view_event", return_value=True)
    def test_get_all_events_accessible(self, mock_can_view_event):
        """Test that all events are returned when the user has access to all."""
        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[self.event1.id, self.event2.id, self.event3.id],
            detailed=False,
        )
        self.assertEqual(len(result), 3)
        self.assertIn(self.event1.id, result)
        self.assertIn(self.event2.id, result)
        self.assertIn(self.event3.id, result)

    @patch("Glassync.database.event.services.can_view_event")
    def test_get_some_events_accessible(self, mock_can_view_event):
        """Test that only accessible events are returned."""
        def side_effect(user_uid, event_id):
            return event_id in [self.event1.id, self.event3.id]

        mock_can_view_event.side_effect = side_effect

        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[self.event1.id, self.event2.id, self.event3.id],
            detailed=False,
        )
        self.assertEqual(len(result), 2)
        self.assertIn(self.event1.id, result)
        self.assertIn(self.event3.id, result)
        self.assertNotIn(self.event2.id, result)

    @patch("Glassync.database.event.services.can_view_event", return_value=False)
    def test_no_events_accessible(self, mock_can_view_event):
        """Test that no events are returned when the user has no access."""
        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[self.event1.id, self.event2.id, self.event3.id],
            detailed=False,
        )
        self.assertEqual(result, {})

    @patch("Glassync.database.event.services.can_view_event", return_value=True)
    def test_detailed_events(self, mock_can_view_event):
        """Test that detailed event data is returned when detailed=True."""
        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[self.event1.id, self.event2.id],
            detailed=True,
        )
        self.assertEqual(len(result), 2)
        self.assertIn(self.event1.id, result)
        self.assertIn("description", result[self.event1.id])
        self.assertIn("recurrence_rule_type", result[self.event1.id])
        self.assertEqual(result[self.event1.id]["id"], self.event1.id)
        self.assertIn("description", result[self.event2.id])
        self.assertEqual(result[self.event2.id]["id"], self.event2.id)

    @patch("Glassync.database.event.services.can_view_event", return_value=True)
    def test_non_detailed_events(self, mock_can_view_event):
        """Test that non-detailed event data is returned when detailed=False."""
        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[self.event1.id, self.event2.id],
            detailed=False,
        )
        self.assertEqual(len(result), 2)
        self.assertIn(self.event1.id, result)
        self.assertNotIn("description", result[self.event1.id])
        self.assertIn("id", result[self.event1.id])
        self.assertIn("name", result[self.event1.id])
        self.assertEqual(result[self.event1.id]["id"], self.event1.id)
        self.assertNotIn("description", result[self.event2.id])
        self.assertEqual(result[self.event2.id]["id"], self.event2.id)

    @patch("Glassync.database.event.services.can_view_event")
    def test_no_matching_event_ids(self, mock_can_view_event):
        """Test that no events are returned when no event IDs match."""
        mock_can_view_event.return_value = True
        result = get_event_by_uids(
            user_uid=self.user1.id,
            event_uids=[999, 1000],  # Non-existent event IDs
            detailed=False,
        )
        self.assertEqual(result, {})