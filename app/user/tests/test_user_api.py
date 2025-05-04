"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


# Generate the URL for the user creation endpoint using the view name 'user:create'
CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return a new user"""
    # Create a new user using the custom user model in models.py and return it
    # The password will be hashed and validated appropriately
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        # Set up an API client to simulate requests
        self.client = APIClient()

    def test_create_user_success(self):
        """Test that creating a user via the API is successful"""
        # Payload with sample user data
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # Send a POST request to the user creation endpoint
        res = self.client.post(CREATE_USER_URL, payload)

        # Check that the response has HTTP 201 Created status
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Fetch the user from the database to confirm creation
        user = get_user_model().objects.get(email=payload['email'])

        # Confirm that the password was correctly hashed and stored
        self.assertTrue(user.check_password(payload['password']))

        # Ensure the password field is not included in the response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email already exists"""
        # Define user data
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        # Create a user directly in the database
        create_user(**payload)

        # Attempt to create the same user via the API
        res = self.client.post(CREATE_USER_URL, payload)

        # Expect a 400 Bad Request due to duplicate email
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if the password is less than 5 characters"""
        # Define user data with a short password
        payload = {
            'email': 'test@example.com',
            'password': 'pw',  # too short
            'name': 'Test Name',
        }

        # Send POST request with invalid password
        res = self.client.post(CREATE_USER_URL, payload)

        # Expect a 400 Bad Request due to password validation
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Confirm the user was not created in the database
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
