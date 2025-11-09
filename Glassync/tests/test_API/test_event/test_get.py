import json
from django.test import TestCase, Client
from django.urls import reverse
from Glassync.models import User, Event, EventMember
from Glassync.database.friendship.services import request_friendship, accept_friendship, check_status, are_friends
from unittest.mock import patch


class GetEventsTests(TestCase):
    def setUp(self):
        """
        Set up the test client and create a user for authentication.
        """
        self.client = Client()
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        self.client.force_login(self.user)
        self.url = reverse("event:get")

    def test_get_events_by_uids_valid(self):
        """
        Test retrieving events by event_uids with valid input.
        """
        # Create an event in the database
        event1 = Event.objects.create(
            id=1,
            name="Event 1",
            date="2025-05-15",
            time_start="10:00:00",
            time_end="12:00:00",
            description="Description of Event 1",
            creator_id=self.user.id,
            recurrence_rule_type=None,
            recurrence_rule_interval=None
        )

        # Send POST request
        response = self.client.post(
            self.url,
            data=json.dumps({
                "event_uids": [1],
                "detailed": True
            }),
            content_type="application/json"
        )

        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "events": {
                "1": {
                    "id": event1.id,
                    "name": event1.name,
                    "date": str(event1.date),
                    "time_start": str(event1.time_start),
                    "time_end": str(event1.time_end),
                    "description": event1.description,
                    "creator_id": event1.creator_id,
                    "recurrence_rule_type": event1.recurrence_rule_type,
                    "recurrence_rule_interval": event1.recurrence_rule_interval,
                    "notifications": None
                }
            }
        })

    def test_get_events_by_user_and_date_valid(self):
        """
        Test retrieving events by user_uid and date range with valid input.
        """
        # Create a second user to represent user_uid=42
        user_42 = User.objects.create(
            id=42,
            first_name="User42",
            last_name="Test",
            email="user42@example.com"
        )

        request_friendship(self.user, user_42)
        accept_friendship(self.user, user_42)
        self.assertEqual(True, are_friends(self.user, user_42))

        # Create an event that fits the time period
        event_in_range = Event.objects.create(
            id=2,
            name="Event 2",
            date="2025-05-20",
            time_start="14:00:00",
            time_end="16:00:00",
            description="Description of Event 2",
            creator_id=self.user.id
        )

        # Create an EventMember entry to associate the event with user_42
        EventMember.objects.create(
            id_event=event_in_range,
            id_user=user_42,  # Associate with user_42
            accept_invitation=True
        )

        # Create an event that does NOT fit the time period
        event_out_of_range = Event.objects.create(
            id=3,
            name="Event 3",
            date="2025-06-01",  # Out of the date range
            time_start="10:00:00",
            time_end="12:00:00",
            description="Description of Event 3",
            creator_id=self.user.id
        )

        # Create an EventMember entry to associate the out-of-range event with user_42
        EventMember.objects.create(
            id_event=event_out_of_range,
            id_user=user_42,  # Associate with user_42
            accept_invitation=True
        )

        # Create an event that fits the time period but belongs to a different user
        event_different_user = Event.objects.create(
            id=4,
            name="Event 4",
            date="2025-05-25",
            time_start="10:00:00",
            time_end="11:00:00",
            description="Description of Event 4",
            creator_id=self.user.id
        )

        # Create a third user to represent user_uid=99
        user_99 = User.objects.create(
            id=99,
            first_name="User99",
            last_name="Test",
            email="user99@example.com"
        )

        # Create an EventMember entry to associate the event with user_99
        EventMember.objects.create(
            id_event=event_different_user,
            id_user=user_99,  # Associate with user_99
            accept_invitation=True
        )

        # Send POST request
        response = self.client.post(
            self.url,
            data=json.dumps({
                "own_uid": 1,
                "user_uid": 42,
                "start_date": "2025-05-01",
                "end_date": "2025-05-31",
                "detailed": True
            }),
            content_type="application/json"
        )

        # Assert response status code
        self.assertEqual(response.status_code, 200)

        # Parse response content
        response_data = json.loads(response.content)

        # Assert response content contains expected fields
        self.assertEqual(len(response_data["events"]), 1)

        # Access the event by iterating through the dictionary
        event_id = list(response_data["events"].keys())[0]  # Get the first event ID
        event = response_data["events"][event_id]  # Access the event by its ID

        # Validate the event fields
        self.assertEqual(int(event_id), event_in_range.id)  # Ensure the event ID matches
        self.assertEqual(event["id"], event_in_range.id)
        self.assertEqual(event["name"], event_in_range.name)
        self.assertEqual(event["date"], str(event_in_range.date))
        self.assertEqual(event["time_start"], str(event_in_range.time_start))
        self.assertEqual(event["time_end"], str(event_in_range.time_end))
        self.assertEqual(event["description"], event_in_range.description)

    def test_invalid_json(self):
        """
        Test request with invalid JSON data.
        """
        response = self.client.post(self.url, data="invalid json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid JSON data"})

    def test_missing_event_uids_and_user_uid(self):
        """
        Test request with missing both event_uids and user_uid.
        """
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            "error": 'Invalid input. Provide either "event_uids" or "user_uid" with date range.'
        })

    def test_invalid_date_format(self):
        """
        Test request with an invalid date format for start_datetime or end_datetime.
        """
        response = self.client.post(
            self.url,
            data=json.dumps({
                "user_uid": 42,
                "start_date": "2025/05/01",
                "end_date": "2025-05-31"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.json()["error"])

    def test_invalid_request_method(self):
        """
        Test using a method other than POST.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Invalid request method, only POST is allowed"})

    @patch("Glassync.models.Event.objects.filter")
    def test_get_events_by_uids_empty_list(self, mock_filter):
        """
        Test retrieving events by event_uids with an empty list.
        """
        mock_filter.return_value = []
        response = self.client.post(
            self.url,
            data=json.dumps({
                "event_uids": [],
                "detailed": True
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"events": {}})

    @patch("Glassync.models.Event.objects.filter")
    def test_get_events_by_user_and_date_no_results(self, mock_filter):
        """
        Test retrieving events by user_uid and date range with no matching results.
        """
        mock_filter.return_value = []
        response = self.client.post(
            self.url,
            data=json.dumps({
                "user_uid": 42,
                "start_date": "2025-05-01",
                "end_date": "2025-05-31"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"events": {}})
