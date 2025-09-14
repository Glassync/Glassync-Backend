from django.test import TestCase, Client
from django.urls import reverse
from Glassync.models import User, Event


class TestApiEventCreate(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )

        # Log in the user (if authentication is required)
        self.client.force_login(self.user)

        # Define the endpoint for the 'create' function
        self.url = reverse('event:create')

        # Define valid event data
        self.valid_event_data = {
            "name": "Test Event",
            "description": "This is a test event",
            "date": "2025-05-15",
            "time_start": "10:00:00",
            "time_end": "11:00:00",
            "recurrence_rule_type": "weekly",
            "recurrence_rule_interval": 1
        }

    def test_conflicting_time_start_and_time_end(self):
        """Test creating an event where time_start is after time_end."""
        data = self.valid_event_data.copy()
        data['time_start'] = '12:00:00'
        data['time_end'] = '10:00:00'  # Invalid: start time is after end time
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_invalid_recurrence_rule_type(self):
        """Test creating an event with an invalid recurrence_rule_type."""
        data = self.valid_event_data.copy()
        data['recurrence_rule_type'] = 'invalid-rule'  # Invalid recurrence rule
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_negative_recurrence_rule_interval(self):
        """Test creating an event with a negative recurrence_rule_interval."""
        data = self.valid_event_data.copy()
        data['recurrence_rule_interval'] = -1  # Invalid: interval cannot be negative
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_large_recurrence_rule_interval(self):
        """Test creating an event with an excessively large recurrence_rule_interval."""
        data = self.valid_event_data.copy()
        data['recurrence_rule_interval'] = 1000000  # Arbitrarily large interval
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_missing_optional_fields(self):
        """Test creating an event with only the required fields."""
        data = {
            "name": "Minimal Event",
            "date": "2025-05-15"
        }  # No description, time_start, time_end, or recurrence_rule
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertIn('event_id', response.json())
        self.assertEqual(Event.objects.count(), 1)

    def test_empty_name_field(self):
        """Test creating an event with an empty name field."""
        data = self.valid_event_data.copy()
        data['name'] = ''  # Empty name is invalid
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_non_json_content_type(self):
        """Test creating an event with a non-JSON content type."""
        response = self.client.post(self.url, self.valid_event_data, content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Event.objects.count(), 0)

    def test_duplicate_event_creation(self):
        """Test creating an event with identical data to an existing event."""
        self.client.post(self.url, self.valid_event_data, content_type='application/json')
        response = self.client.post(self.url, self.valid_event_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)  # Still valid unless business logic dictates otherwise
        self.assertEqual(Event.objects.count(), 2)  # Check if duplicates are allowed

    def test_unauthenticated_user(self):
        """Test creating an event without being logged in."""
        self.client.logout()  # Log out the user
        response = self.client.post(self.url, self.valid_event_data, content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login for unauthenticated user
        self.assertEqual(Event.objects.count(), 0)