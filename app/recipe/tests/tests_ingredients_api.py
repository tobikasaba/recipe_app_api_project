"""
Tests for the ingredients API
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Create and return a URL ingredient detail endpoint"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        # Create a test user and authenticate the test client
        self.user = create_user()
        # initiate a DRF API client
        self.client = APIClient()
        # log in as that user
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        # Create sample ingredients for the authenticated user
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        # Make GET request to ingredient list endpoint
        res = self.client.get(INGREDIENTS_URL)

        # Fetch and serialise the expected ingredient objects
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        # Verify the response matches the serialised data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""
        # Create a second user and an ingredient for them
        user2 = create_user(email="user2@exmaple.com")
        Ingredient.objects.create(user=user2, name="Salt")

        # Create an ingredient for the authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        # Make GET request to retrieve ingredients
        res = self.client.get(INGREDIENTS_URL)

        # Ensure only the authenticated user's ingredients are returned
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        # Create an ingredient for our authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name="Cilantro")

        # Define the new name in the payload
        payload = {"name": "Coriander"}
        # Build the detail URL for this ingredient
        url = detail_url(ingredient.id)
        # Send a PATCH request with the update
        res = self.client.patch(url, payload)

        # Expect a 200 OK response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Reload the ingredient from the DB
        ingredient.refresh_from_db()
        # Check that the name was updated correctly
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Testing deleting an ingredient"""
        # Create an ingredient for the authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name="Lettuce")

        # Build the detail URL for deletion
        url = detail_url(ingredient.id)
        # Send a DELETE request to remove the ingredient
        res = self.client.delete(url)

        # Expect a 204 No Content response on successful deletion
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm the ingredient has been removed from the database
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        # create the first ingredient
        in1 = Ingredient.objects.create(user=self.user, name="Apples")
        # create a second ingredient
        in2 = Ingredient.objects.create(user=self.user, name="Turkey")

        # create a recipe and link only the first ingredient to it
        recipe = Recipe.objects.create(
            title="Apple crumble",
            time_minutes=5,
            price=Decimal("4.50"),
            user=self.user,
        )
        recipe.ingredients.add(in1)  # assign “Apples” to the recipe

        # call the API with the assigned_only filter
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        # serialise each ingredient for comparison
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        # Confirm “Apples” is present
        self.assertIn(s1.data, res.data)
        # Confirm “Turkey” is absent
        self.assertNotIn(s2.data, res.data)

    # Test that the same ingredient appears only once when assigned to multiple recipes
    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        # Create one ingredient to be shared, and one unassigned
        ing = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Lentils")

        # create two recipes, both using the “Eggs” ingredient
        recipe1 = Recipe.objects.create(
            title="Eggs benedict",
            time_minutes=30,
            price=Decimal("7.00"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Herb Eggs",
            time_minutes=20,
            price=Decimal("4.00"),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        # call the API with the same assigned_only filter
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        # expect exactly one entry for “Eggs”, not two
        self.assertEqual(len(res.data), 1)
