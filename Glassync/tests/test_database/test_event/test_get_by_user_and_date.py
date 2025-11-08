from datetime import date
from django.test import TestCase
from Glassync.models import Event, EventMember, User
from Glassync.database.event.services import get_event_by_user_and_date, are_friends
from unittest.mock import patch


class TestGetEventByUserAndDate(TestCase):
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
        self.user3 = User.objects.create(
            first_name="Charlie",
            last_name="Brown",
            email="charlie@example.com"
        )

        # Create test events
        self.event1 = Event.objects.create(
            id=101,
            name="Event Created by Alice",
            description="Alice's event",
            date=date(2025, 5, 20),
            time_start="10:00:00",
            time_end="12:00:00",
            recurrence_rule_type="daily",
            recurrence_rule_interval=1,
            creator=self.user1
        )
        self.event2 = Event.objects.create(
            id=102,
            name="Event Created by Bob",
            description="Bob's event",
            date=date(2025, 5, 21),
            time_start="14:00:00",
            time_end="16:00:00",
            recurrence_rule_type="weekly",
            recurrence_rule_interval=2,
            creator=self.user2
        )

        # Add user3 as a member of event2
        self.event_member = EventMember.objects.create(
            id_event=self.event2,
            id_user=self.user3,
            accept_invitation=True
        )

    @patch("Glassync.database.event.services.are_friends", return_value=False)
    def test_no_access(self, mock_are_friends):
        """Test that no events are returned if the user does not have access."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user3.id,
            start_date=date(2025, 5, 19),
            end_date=date(2025, 5, 22),
        )
        self.assertEqual(result, {})

    @patch("Glassync.database.event.services.are_friends", return_value=True)
    def test_access_as_friend(self, mock_are_friends):
        """Test that events are returned if the requesting user is a friend."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user3.id,
            start_date=date(2025, 5, 19),
            end_date=date(2025, 5, 22),
        )
        self.assertEqual(len(result), 1)
        self.assertIn(self.event2.id, result)
        self.assertEqual(result[self.event2.id]["id"], self.event2.id)

    def test_access_as_self(self):
        """Test that events are returned if the requesting user is the same as the user_uid."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user1.id,
            start_date=date(2025, 5, 19),
            end_date=date(2025, 5, 22),
        )
        self.assertEqual(len(result), 1)
        self.assertIn(self.event1.id, result)
        self.assertEqual(result[self.event1.id]["id"], self.event1.id)

    def test_events_detailed(self):
        """Test that detailed event data is returned when detailed=True."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user1.id,
            start_date=date(2025, 5, 19),
            end_date=date(2025, 5, 22),
            detailed=True,
        )
        self.assertEqual(len(result), 1)
        self.assertIn(self.event1.id, result)
        event = result[self.event1.id]
        self.assertIn("description", event)
        self.assertIn("recurrence_rule_type", event)
        self.assertEqual(event["id"], self.event1.id)

    def test_events_non_detailed(self):
        """Test that non-detailed event data is returned when detailed=False."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user1.id,
            start_date=date(2025, 5, 19),
            end_date=date(2025, 5, 22),
            detailed=False,
        )
        self.assertEqual(len(result), 1)
        self.assertIn(self.event1.id, result)
        event = result[self.event1.id]
        self.assertNotIn("description", event)
        self.assertIn("id", event)
        self.assertIn("name", event)
        self.assertEqual(event["id"], self.event1.id)

    def test_no_events_in_date_range(self):
        """Test that no events are returned if none exist in the given date range."""
        result = get_event_by_user_and_date(
            own_uid=self.user1.id,
            user_uid=self.user1.id,
            start_date=date(2025, 5, 22),
            end_date=date(2025, 5, 23),
        )
        self.assertEqual(result, {})
