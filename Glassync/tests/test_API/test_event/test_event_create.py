from django.test import TestCase, Client
from django.urls import reverse
from Glassync.models import User, Event

class EventCreateAPITestCase(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password_hash="hashedpassword"
        )

        # Define the endpoint for the 'create' function
        self.url = reverse('event:create')

        # Define valid event data
        self.valid_event_data = {
            "creator_id": self.user.id,
            "name": "Test Event",
            "description": "This is a test event",
            "date": "2025-05-15",
            "time_start": "10:00:00",
            "time_end": "11:00:00",
            "recurrence_rule_type": "weekly",
            "recurrence_rule_interval": 1
        }

    def test_create_event_success(self):
        """Test creating an event with valid data."""
        response = self.client.post(self.url, self.valid_event_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertIn('event_id', response.json())
        self.assertEqual(Event.objects.count(), 1)

    def test_missing_required_fields(self):
        """Test creating an event with missing required fields."""
        data = self.valid_event_data.copy()
        del data['name']  # Remove a required field
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_invalid_date_format(self):
        """Test creating an event with an invalid date format."""
        data = self.valid_event_data.copy()
        data['date'] = 'invalid-date'  # Invalid date format
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_invalid_time_format(self):
        """Test creating an event with an invalid time format."""
        data = self.valid_event_data.copy()
        data['time_start'] = 'invalid-time'  # Invalid time format
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_creator_not_found(self):
        """Test creating an event when the creator does not exist."""
        data = self.valid_event_data.copy()
        data['creator_id'] = 9999  # Non-existent creator ID
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_empty_request_body(self):
        """Test creating an event with an empty request body."""
        response = self.client.post(self.url, {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_invalid_request_method(self):
        """Test using a request method other than POST."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())