"""
Tests for the tags API
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail URL"""
    # Look up the URL for the 'recipe:tag-detail' route,
    # inserting the tag’s ID into the URL pattern
    return reverse(
        "recipe:tag-detail",  # The named URL pattern defined in the router
        args=[tag_id],  # Positional arguments to fill in the URL’s parameters
    )


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        # Instantiate a DRF test client for making unauthenticated requests
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving tags"""
        # Send a GET to the tags endpoint without credentials
        res = self.client.get(TAGS_URL)
        # Expect a 401 Unauthorised response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        # Create and store a test user
        self.user = create_user()
        # Initialise a  DRF test client
        self.client = APIClient()
        # Force authentication for this client as the test user
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        # Create two tags for our authenticated user
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # Retrieve the list of tags
        res = self.client.get(TAGS_URL)

        # Query & serialize tags ordered by name descending
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        # Expect a 200 OK response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ensure the response data matches our serialized data
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""

        # Create a second user and a tag for them.
        # *NOTE* django model manager (named 'objects') has an inbuilt create function
        user2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user2, name="Fruity")
        # Create a tag for our authenticated user
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        # Retrieve the list of tags again
        res = self.client.get(TAGS_URL)

        # Expect a 200 OK response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only one tag should be returned
        self.assertEqual(len(res.data), 1)

        #  Verify the returned tag’s ID and name matches the expected results
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        # Create a tag for the authenticated user with an initial name
        tag = Tag.objects.create(user=self.user, name="After dinner")

        # Define the new data we want to apply
        payload = {"name": "Desert"}

        # Build the URL for this tag’s detail endpoint
        url = detail_url(tag.id)

        # Send a PATCH request to update the tag’s name
        res = self.client.patch(url, payload)

        # Expect a 200 OK response indicating success
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the tag instance from the database to pick up changes
        tag.refresh_from_db()

        # Check that the tag’s name was updated correctly
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag"""
        # Create a tag for the authenticated user
        tag = Tag.objects.create(user=self.user, name="After dinner")

        # Build the URL for this tag’s detail endpoint
        url = detail_url(tag.id)

        # Send a DELETE request to remove the tag
        res = self.client.delete(url)

        # Expect a 204 No Content response signalling successful deletion
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Query the database for the tag by its ID
        tags = Tag.objects.filter(id=tag.id)

        # Confirm that the tag no longer exists
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes"""
        # Create the first tag
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        # Create a second tag
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        # create a recipe and link only the first tag to it
        recipe = Recipe.objects.create(
            title="Green Eggs on Toast",
            time_minutes=10,
            price=Decimal("2.50"),
            user=self.user,
        )
        recipe.tags.add(tag1)  # assign "Breakfast" to the recipe

        # Request tags, filtering only those assigned to recipes
        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        # Serialize each tag for comparison
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        # Confirm “Breakfast” is present
        self.assertIn(s1.data, res.data)
        # Confirm “Lunch” is absent
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list"""
        # Create one tag to be shared, and one unassigned
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Dinner")

        # Create two recipes, both using the same Breakfast tag
        recipe1 = Recipe.objects.create(
            title="Pancakes",
            time_minutes=5,
            price=Decimal("5.00"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Porridge",
            time_minutes=3,
            price=Decimal("2.00"),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        # Request tags with the assigned_only filter
        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        # expect exactly one entry for “Breakfast”, not two
        self.assertEqual(len(res.data), 1)
