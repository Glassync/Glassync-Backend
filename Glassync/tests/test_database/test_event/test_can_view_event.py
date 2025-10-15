from django.test import TestCase
from Glassync.models import Event, EventMember, User
from Glassync.database.event.services import can_view_event


class TestCanViewEvent(TestCase):
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
            name="Event Created by Alice",
            description="This is Alice's event.",
            date="2025-05-15",
            time_start="10:00:00",
            time_end="12:00:00",
            creator=self.user1
        )
        self.event2 = Event.objects.create(
            name="Event Created by Bob",
            description="This is Bob's event.",
            date="2025-05-20",
            time_start="14:00:00",
            time_end="16:00:00",
            creator=self.user2
        )

        # Create event members
        self.event_member = EventMember.objects.create(
            id_event=self.event2,
            id_user=self.user3,
            accept_invitation=True
        )

    def test_user_is_creator(self):
        """Test that the user can view the event if they are the creator."""
        # Alice is the creator of event1
        result = can_view_event(user_id=self.user1.id, event_id=self.event1.id)
        self.assertTrue(result)

    def test_user_is_member(self):
        """Test that the user can view the event if they are a member."""
        # Charlie is a member of event2
        result = can_view_event(user_id=self.user3.id, event_id=self.event2.id)
        self.assertTrue(result)

    def test_user_is_not_creator_or_member(self):
        """Test that the user cannot view the event if they are neither the creator nor a member."""
        # Alice is neither the creator nor a member of event2
        result = can_view_event(user_id=self.user1.id, event_id=self.event2.id)
        self.assertFalse(result)

    def test_event_does_not_exist(self):
        """Test that the function returns False if the event does not exist."""
        # Event ID 9999 does not exist
        result = can_view_event(user_id=self.user1.id, event_id=9999)
        self.assertFalse(result)

    def test_user_does_not_exist(self):
        """Test that the function returns False if the user does not exist."""
        # User ID 9999 does not exist
        result = can_view_event(user_id=9999, event_id=self.event1.id)
        self.assertFalse(result)