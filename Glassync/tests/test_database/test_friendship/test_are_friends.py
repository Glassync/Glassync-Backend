from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import are_friends


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
        self.user5 = User.objects.create(
            first_name="Eve",
            last_name="Adams",
            email="eve@example.com"
        )

        # Create relationships
        UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=True  # Friends
        )
        UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user3,
            status_user1=True,
            status_user2=False  # Friend request sent
        )
        UsersRelationship.objects.create(
            id_user1=self.user4,
            id_user2=self.user1,
            status_user1=True,
            status_user2=False  # Friend request received
        )
        # No relationship between user1 and user5

    def test_are_friends_true(self):
        """Test that are_friends returns True for users who are friends."""
        result = are_friends(self.user1, self.user2)
        self.assertTrue(result)

    def test_are_friends_false_friend_request_sent(self):
        """Test that are_friends returns False for users with a sent friend request."""
        result = are_friends(self.user1, self.user3)
        self.assertFalse(result)

    def test_are_friends_false_friend_request_received(self):
        """Test that are_friends returns False for users with a received friend request."""
        result = are_friends(self.user4, self.user1)
        self.assertFalse(result)

    def test_are_friends_false_no_relationship(self):
        """Test that are_friends returns False for users with no relationship."""
        result = are_friends(self.user1, self.user5)
        self.assertFalse(result)

    def test_are_friends_symmetry(self):
        """Test that are_friends is symmetric for users who are friends."""
        result1 = are_friends(self.user1, self.user2)  # user1 -> user2
        result2 = are_friends(self.user2, self.user1)  # user2 -> user1
        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_are_friends_symmetry_false(self):
        """Test that are_friends is symmetric for users who are not friends."""
        result1 = are_friends(self.user3, self.user1)  # user3 -> user1
        result2 = are_friends(self.user1, self.user3)  # user1 -> user3
        self.assertFalse(result1)
        self.assertFalse(result2)