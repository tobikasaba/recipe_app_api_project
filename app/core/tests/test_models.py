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

    def test_new_user_email_normalised(self):
        """Test email is normalised for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        # Syntax for looping through a list containing multiple sublists (tuples or lists).
        # 'email' is assigned the first item in each sublist, and 'expected' the second.
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without aan email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """Test creating a supersuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        # is_superuser is inbuilt in django's permission system'
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
