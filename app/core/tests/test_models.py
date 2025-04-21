"""
Tests for models
"""

from django.test import TestCase

# used get the default user model for the project
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models functions"""

    # checks that we can create a user with an email successfully
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'

        # Use the create_user method from the custom user model's manager
        # call the create_user method on the model manager to create a user with the email and password
        # objets is a reference to the manager created
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        # Check that the user was created with the correct email
        self.assertEqual(user.email, email)
        # Check that the password is hashed and not stored in plain text
        self.assertTrue(user.check_password(password))
