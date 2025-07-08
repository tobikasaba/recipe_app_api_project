"""
Tests for models
"""

from decimal import Decimal
from django.test import TestCase

# used get the default user model for the project
from django.contrib.auth import get_user_model
from core import models


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models functions"""

    # checks that we can create a user with an email successfully
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"

        # Use the create_user method from the custom user model's manager
        # call the create_user method on the model manager to create a user with the email and password
        # objets is a reference to the manager created
        user = get_user_model().objects.create_user(email=email, password=password)

        # Check that the user was created with the correct email
        self.assertEqual(user.email, email)
        # Check that the password is hashed and not stored in plain text
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test email is normalised for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@EXAMPLE.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        # Syntax for looping through a list containing multiple sublists (tuples or lists).
        # 'email' is assigned the first item in each sublist, and 'expected' the second.
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without aan email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_superuser(self):
        """Test creating a supersuser"""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        # is_superuser is inbuilt in django's permission system'
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        # creates a new user which creates the recipe
        user = get_user_model().objects.create_user("test@example.com", "testpass123")

        # creates a new recipe using the Recipe model
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description",
        )

        # Tests the string representation (__str__) of the recipe.
        # Assumes __str__ in the Recipe model returns the recipe's title.
        # If str(recipe) is not equal to recipe.title, this test will fail.
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()

        # Create and save a new Tag, linking it to our test user
        tag = models.Tag.objects.create(
            user=user,  # Assign the tag to the user we just created
            name="Tag1",  # Give the tag the name "Tag1"
        )

        # Verify that the tag’s __str__ output matches its name
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful"""
        user = create_user()

        ingredient = models.Ingredient.objects.create(user=user, name="Ingredient1")
        self.assertEqual(str(ingredient), ingredient.name)
