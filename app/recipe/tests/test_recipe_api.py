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


# Returns the detail URL for a specific recipe using its ID
# Used in tests to easily construct the endpoint for retrieving/updating/deleting a specific recipe
def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='user@example.com', password='test123')
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
        other_user = create_user(
            email='other@example.com', password='test123')
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

    def test_create_recipe(self):
        """Test creating a recipe"""

        # Define the payload (data to be sent in the request)
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        # Send a POST request to create a new recipe with the payload
        res = self.client.post(RECIPES_URL, payload)

        # Check that the response status is 201 CREATED (success)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the recipe object from the database using the returned ID
        recipe = Recipe.objects.get(id=res.data['id'])

        # Loop through the original payload and confirm each field matches the created recipe
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        # Confirm the recipe was created for the logged-in user
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        # Define a known link so we can check it doesn’t change
        original_link = 'https://example.com/recipe.pdf'
        # Create a recipe for the authenticated user with a specific title and link
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link
        )

        # Prepare partial update data (only the title)
        payload = {'title': 'New recipe title'}
        # Build the URL for this recipe’s detail endpoint
        url = detail_url(recipe.id)
        # Send a PATCH request to update just the title field
        res = self.client.patch(url, payload)

        # Expect HTTP 200 OK for a successful partial update
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Reload the recipe from the database to see the changes
        recipe.refresh_from_db()
        # Check that the title was updated correctly
        self.assertEqual(recipe.title, payload['title'])
        # Ensure the link was left unchanged by the partial update
        self.assertEqual(recipe.link, original_link)
        # Confirm the recipe still belongs to the same authenticated user
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe"""
        # Create a recipe with an initial title, link and description
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com',
            description='Sample recipe description'
        )

        # Full payload to replace every field of the recipe
        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50')
        }

        # Construct the detail URL and send a PUT request with the full payload
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        # Expect HTTP 200 OK for a successful full update
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Refresh from the database to retrieve updated values
        recipe.refresh_from_db()
        # Verify each field in the payload matches the recipe’s attributes
        for (k, v) in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        # Ensure ownership remains with the authenticated user
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        # Create a second user in the test database
        new_user = create_user(email='user2@example.com', password='test123')
        # Create a recipe owned by the original authenticated user
        recipe = create_recipe(user=self.user)

        # Attempt to change ownership by sending the new user’s ID
        payload = {'user': new_user.id}
        # Build the detail URL for this recipe
        url = detail_url(recipe.id)
        # Send a PATCH request; ownership change should be ignored or rejected
        self.client.patch(url, payload)

        # Refresh the recipe from the database to pick up any changes
        recipe.refresh_from_db()
        # The owner must remain the original user
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        # Create a recipe owned by the authenticated user
        recipe = create_recipe(user=self.user)

        # Build the detail URL for this recipe
        url = detail_url(recipe.id)
        # Send a DELETE request to remove the recipe
        res = self.client.delete(url)

        # Expect HTTP 204 No Content for a successful deletion
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Verify the recipe no longer exists in the database
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        # Create a second user
        new_user = create_user(email='user2@example.com', password='test123')
        # Create a recipe owned by that second user
        recipe = create_recipe(user=new_user)

        # Build the detail URL for that recipe
        url = detail_url(recipe.id)
        # The first (authenticated) user tries to delete it
        res = self.client.delete(url)

        # Expect HTTP 404 Not Found, as they shouldn’t have access
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # Ensure the recipe still exists in the database
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
