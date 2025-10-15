from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import accept_friendship, check_status


class Tests(TestCase):
    def setUp(self):
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
        self.friend_request = UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=False  # Friend request sent
        )
        self.already_friends = UsersRelationship.objects.create(
            id_user1=self.user2,
            id_user2=self.user3,
            status_user1=True,
            status_user2=True  # Already friends
        )

    def test_accept_friendship_success(self):
        """Test that a friendship request is successfully accepted."""
        # Check initial status
        initial_status = check_status(self.user1, self.user2)
        self.assertEqual(initial_status, "friend_request_sent")

        # Perform the action
        result = accept_friendship(self.user1, self.user2)
        self.assertTrue(result)

        # Verify that the relationship has been updated
        updated_status = check_status(self.user1, self.user2)
        self.assertEqual(updated_status, "friends")

    def test_accept_friendship_no_request(self):
        """Test that accepting friendship fails when no request exists."""
        # Check initial status
        initial_status = check_status(self.user3, self.user4)
        self.assertEqual(initial_status, "not_friends")

        # Perform the action
        result = accept_friendship(self.user3, self.user4)
        self.assertFalse(result)

        # Verify that the status remains unchanged
        updated_status = check_status(self.user3, self.user4)
        self.assertEqual(updated_status, "not_friends")

    def test_accept_friendship_already_friends(self):
        """Test that accepting friendship fails when users are already friends."""
        # Check initial status
        initial_status = check_status(self.user2, self.user3)
        self.assertEqual(initial_status, "friends")

        # Perform the action
        result = accept_friendship(self.user2, self.user3)
        self.assertFalse(result)

        # Verify that the status remains unchanged
        updated_status = check_status(self.user2, self.user3)
        self.assertEqual(updated_status, "friends")

    def test_accept_friendship_wrong_direction(self):
        """Test that accepting friendship fails when the request direction is wrong."""
        # Check initial status
        initial_status = check_status(self.user2, self.user1)
        self.assertEqual(initial_status, "friend_request_received")

        # Perform the action
        result = accept_friendship(self.user2, self.user1)  # Reversed direction
        self.assertFalse(result)

        # Verify that the status remains unchanged
        updated_status = check_status(self.user2, self.user1)
        self.assertEqual(updated_status, "friend_request_received")