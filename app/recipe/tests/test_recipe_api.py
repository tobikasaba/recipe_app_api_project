"""
Tests for recipe API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

# a seperate url is created because because each recipe url will be different and you need it to contain the unique id to get the recipe dtail


def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""

    # Default recipe data
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'https://example.com/recipe.pdf'
    }

    # Override any defaults with explicitly passed parameters
    # If no updated recipe parameters are provided when create_recipe is fuction is called,
    # The functions the default parameters defined above
    defaults.update(params)

    # Create a new recipe with the user and final parameters
    recipe = Recipe.objects.create(user=user, **defaults)

    # Return the newly created recipe object
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        # Instantiate an APIClient without authentication
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        # Attempt to GET recipes without logging in
        res = self.client.get(RECIPES_URL)
        # Expect a 401 Unauthorized response
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        # Instantiate an APIClient
        self.client = APIClient()
        # Create and save a user
        self.user = get_user_model().objects.create_user(
            'user@example.com', 'testpass123'
        )
        # Force authentication for all requests using this client
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes"""
        # Create two recipes for this authenticated user
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # Send a GET request to the recipes endpoint
        res = self.client.get(RECIPES_URL)

        # Retrieve all recipes from the database, ordered by newest first (id)
        recipes = Recipe.objects.all().order_by('-id')
        # Serialize these recipes for comparison
        # many=True flag tells the serializer that a collection of objects is passed
        serializer = RecipeSerializer(recipes, many=True)

        # Verify the response is HTTP 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify the returned data matches the serialized recipes
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        # Create a recipe for another user
        other_user = get_user_model().objects.create_user(
            'other@example.com', 'password123'
        )
        create_recipe(user=other_user)

        # Create a recipe for the authenticated user
        create_recipe(user=self.user)

        # Send a GET request to the recipes endpoint
        res = self.client.get(RECIPES_URL)

        # Filter recipes so only those owned by the authenticated user remain
        recipes = Recipe.objects.filter(user=self.user)
        # Serialize these filtered recipes
        serializer = RecipeSerializer(recipes, many=True)

        # Verify the response is HTTP 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify only the authenticated user’s recipes are returned
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
