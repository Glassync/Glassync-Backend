from django.test import TestCase
from Glassync.models import UsersRelationship, User
from Glassync.database.friendship.services import get_relationship_row


class Tests(TestCase):
    def setUp(self):
        # Create test users with email as the username
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

        # Create test relationships
        self.relationship1 = UsersRelationship.objects.create(
            id_user1=self.user1,
            id_user2=self.user2,
            status_user1=True,
            status_user2=False
        )

    def test_relationship_exists(self):
        """Test that the function returns the correct relationship when it exists."""
        relationship, user1_status, user2_status = get_relationship_row(self.user1, self.user2)

        self.assertIsNotNone(relationship)
        self.assertEqual(relationship, self.relationship1)
        self.assertEqual(user1_status, True)
        self.assertEqual(user2_status, False)

    def test_relationship_does_not_exist(self):
        """Test that the function returns (None, None, None) when no relationship exists."""
        relationship, user1_status, user2_status = get_relationship_row(self.user1, self.user3)

        self.assertIsNone(relationship)
        self.assertIsNone(user1_status)
        self.assertIsNone(user2_status)

    def test_reverse_relationship_does_not_match(self):
        """
        Test that the function does not find a relationship if the user roles are reversed.
        This ensures the function only matches id_user1 to user1 and id_user2 to user2.
        """
        relationship, user1_status, user2_status = get_relationship_row(self.user2, self.user1)

        self.assertIsNone(relationship)
        self.assertIsNone(user1_status)
        self.assertIsNone(user2_status)
