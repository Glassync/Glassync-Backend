from django.test import TestCase
from Glassync.models import Event, EventMember, User
from Glassync.database.event.services import delete_event


class TestDeleteEvent(TestCase):
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
            name="Event Created by Bob",
            description="This is Bob's event.",
            date="2025-05-16",
            time_start="14:00:00",
            time_end="16:00:00",
            recurrence_rule_type="weekly",
            recurrence_rule_interval=2,
            creator=self.user2
        )

        # Add members to events
        self.event_member1 = EventMember.objects.create(
            id_event=self.event1,
            id_user=self.user2,
            accept_invitation=True
        )
        self.event_member2 = EventMember.objects.create(
            id_event=self.event2,
            id_user=self.user1,
            accept_invitation=True
        )

    def test_delete_event_success(self):
        """Test that the creator can successfully delete an event."""
        # Perform the deletion
        result = delete_event(event_id=self.event1.id, user_id=self.user1.id)
        self.assertIn('message', result)
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], 'Event and associated members deleted successfully')

        # Verify that the event and associated members are deleted
        event_exists = Event.objects.filter(id=self.event1.id).exists()
        self.assertFalse(event_exists)
        members_exist = EventMember.objects.filter(id_event_id=self.event1.id).exists()
        self.assertFalse(members_exist)

    def test_delete_event_permission_denied(self):
        """Test that a non-creator cannot delete an event."""
        # Attempt to delete the event as a non-creator
        result = delete_event(event_id=self.event1.id, user_id=self.user2.id)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 403)
        self.assertEqual(result['error'], 'Permission denied. Only the creator can delete this event.')

        # Verify that the event and its members still exist
        event_exists = Event.objects.filter(id=self.event1.id).exists()
        self.assertTrue(event_exists)
        members_exist = EventMember.objects.filter(id_event_id=self.event1.id).exists()
        self.assertTrue(members_exist)

    def test_delete_event_not_found(self):
        """Test that trying to delete a non-existent event returns a 404 error."""
        # Attempt to delete a non-existent event
        result = delete_event(event_id=9999, user_id=self.user1.id)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 404)
        self.assertEqual(result['error'], 'Event not found')

    def test_delete_event_with_members(self):
        """Test that deleting an event also deletes its associated members."""
        # Perform the deletion
        result = delete_event(event_id=self.event2.id, user_id=self.user2.id)
        self.assertIn('message', result)
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], 'Event and associated members deleted successfully')

        # Verify that the event and associated members are deleted
        event_exists = Event.objects.filter(id=self.event2.id).exists()
        self.assertFalse(event_exists)
        members_exist = EventMember.objects.filter(id_event_id=self.event2.id).exists()
        self.assertFalse(members_exist)