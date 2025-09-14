from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import check_status


class TestCheckStatus(TestCase):
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
        UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=True
        )
        UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user3,
            status_user1=True,
            status_user2=False
        )

    def test_friends_user1_to_user2(self):
        """Test that user1 and user2 are friends."""
        status = check_status(self.user1, self.user2)
        self.assertEqual(status, "friends")

    def test_friends_user2_to_user1(self):
        """Test that user2 and user1 are friends when the order is reversed."""
        status = check_status(self.user2, self.user1)
        self.assertEqual(status, "friends")

    def test_friend_request_sent_user1_to_user3(self):
        """Test that user1 sent a friend request to user3."""
        status = check_status(self.user1, self.user3)
        self.assertEqual(status, "friend_request_sent")

    def test_friend_request_received_user3_to_user1(self):
        """Test that user1 received a friend request from user3."""
        status = check_status(self.user3, self.user1)
        self.assertEqual(status, "friend_request_received")

    def test_no_relationship_user1_to_user4(self):
        """Test that user1 has no relationship with user4."""
        status = check_status(self.user1, self.user4)
        self.assertEqual(status, "not_friends")

    def test_no_relationship_user4_to_user1(self):
        """Test that user4 has no relationship with user1 when the order is reversed."""
        status = check_status(self.user4, self.user1)
        self.assertEqual(status, "not_friends")
