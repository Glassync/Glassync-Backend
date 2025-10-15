from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import delete_friendship, check_status


class TestDeleteFriendship(TestCase):
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
        self.user4 = User.objects.create(
            first_name="Daisy",
            last_name="Miller",
            email="daisy@example.com"
        )

        # Create relationships
        self.friends_relationship = UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=True  # They are friends
        )
        self.pending_request = UsersRelationship.objects.create(
            id_user1=self.user3,
            id_user2=self.user4,
            status_user1=True,
            status_user2=False  # Friend request sent
        )

    def test_delete_friendship_success(self):
        """Test that a friendship is successfully deleted."""
        # Check initial status
        initial_status = check_status(self.user1, self.user2)
        self.assertEqual(initial_status, "friends")

        # Perform the action
        result = delete_friendship(self.user1, self.user2)
        self.assertIn('message', result)
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], 'Friendship deleted')

        # Verify that the relationship has been deleted
        relationship_exists = UsersRelationship.objects.filter(id_user1=self.user1, id_user2=self.user2).exists()
        self.assertFalse(relationship_exists)

        # Verify updated status
        updated_status = check_status(self.user1, self.user2)
        self.assertEqual(updated_status, "not_friends")

    def test_delete_friendship_no_relationship(self):
        """Test that deleting fails when no relationship exists."""
        # Check initial status
        initial_status = check_status(self.user1, self.user4)
        self.assertEqual(initial_status, "not_friends")

        # Perform the action
        result = delete_friendship(self.user1, self.user4)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'No friendship found to delete')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user1, self.user4)
        self.assertEqual(updated_status, "not_friends")

    def test_delete_friendship_pending_request(self):
        """Test that deleting fails when there is a pending friendship request."""
        # Check initial status
        initial_status = check_status(self.user3, self.user4)
        self.assertEqual(initial_status, "friend_request_sent")

        # Perform the action
        result = delete_friendship(self.user3, self.user4)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'No friendship found to delete')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user3, self.user4)
        self.assertEqual(updated_status, "friend_request_sent")
