from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import request_friendship, check_status


class TestRequestFriendship(TestCase):
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
        self.already_friends = UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=True  # Already friends
        )
        self.pending_request = UsersRelationship.objects.create(
            id_user1=self.user3,
            id_user2=self.user4,
            status_user1=True,
            status_user2=False  # Friend request sent
        )

    def test_request_friendship_success(self):
        """Test that a friendship request is successfully created."""
        # Check initial status
        initial_status = check_status(self.user1, self.user3)
        self.assertEqual(initial_status, "not_friends")

        # Perform the action
        result = request_friendship(self.user1, self.user3)
        self.assertIn('message', result)
        self.assertNotIn('error', result)
        self.assertEqual(result['status'], 201)
        self.assertEqual(result['message'], 'Friendship request sent')

        # Verify that the relationship has been created
        relationship_exists = UsersRelationship.objects.filter(id_user1=self.user1, id_user2=self.user3).exists()
        self.assertTrue(relationship_exists)

        # Verify updated status
        updated_status = check_status(self.user1, self.user3)
        self.assertEqual(updated_status, "friend_request_sent")

    def test_request_friendship_already_friends(self):
        """Test that friendship request fails when users are already friends."""
        # Check initial status
        initial_status = check_status(self.user1, self.user2)
        self.assertEqual(initial_status, "friends")

        # Perform the action
        result = request_friendship(self.user1, self.user2)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Friendship request could not be created')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user1, self.user2)
        self.assertEqual(updated_status, "friends")

    def test_request_friendship_pending_request(self):
        """Test that friendship request fails when a pending request already exists."""
        # Check initial status
        initial_status = check_status(self.user3, self.user4)
        self.assertEqual(initial_status, "friend_request_sent")

        # Perform the action
        result = request_friendship(self.user3, self.user4)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Friendship request could not be created')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user3, self.user4)
        self.assertEqual(updated_status, "friend_request_sent")

    def test_request_friendship_reverse_request(self):
        """Test that friendship request fails when a reversed pending request exists."""
        # Check initial status
        initial_status = check_status(self.user4, self.user3)
        self.assertEqual(initial_status, "friend_request_received")

        # Perform the action
        result = request_friendship(self.user4, self.user3)  # Reversed direction
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Friendship request could not be created')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user4, self.user3)
        self.assertEqual(updated_status, "friend_request_received")

    def test_request_friendship_self_request(self):
        """Test that friendship request fails when a user tries to request friendship with themselves."""
        # Check initial status
        initial_status = check_status(self.user1, self.user1)
        self.assertEqual(initial_status, "not_friends")

        # Perform the action
        result = request_friendship(self.user1, self.user1)
        self.assertIn('error', result)
        self.assertNotIn('message', result)
        self.assertEqual(result['status'], 400)
        self.assertEqual(result['error'], 'Cannot send a friend request to yourself')

        # Verify that the status remains unchanged
        updated_status = check_status(self.user1, self.user1)
        self.assertEqual(updated_status, "not_friends")
