"""
Views for the recipe APIs

RecipeViewSet extends viewsets.ModelViewSet which provides a set of default actions:
list, create, retrieve, update, partial_update, and destroy.

TagViewSet extends viewsets.GenericViewSet, which by itself does not provide any default actions.

Instead, it gains its behaviour (list, update, destroy) through explicitly added mixins:
ListModelMixin, UpdateModelMixin, and DestroyModelMixin.

GenericViewSet is used when you want fine-grained control over which actions are available,
allowing you to include only specific operations by combining it with the appropriate mixins.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes"""

    # Require token-based authentication
    authentication_classes = [TokenAuthentication]

    # Allow access only to authenticated users
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # Filter the base queryset so users see only their own ingredients
        return self.queryset.filter(user=self.request.user).order_by("-name")


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    # Use the RecipeDetailSerializer to (de)serialize data
    # Use this serializer to convert Recipe objects <-> JSON (to JSON)
    # i.e. Use RecipeDetailSerializer for serialising Recipe instances
    # serializer_class = serializers.RecipeSerializer
    serializer_class = serializers.RecipeDetailSerializer

    # Base queryset of all Recipe instances (Contains all instances, will be scoped per-user)
    queryset = Recipe.objects.all()

    # Require token-based authentication
    authentication_classes = [TokenAuthentication]

    # Allow access only to authenticated users
    permission_classes = [IsAuthenticated]

    # Overrides the default get_queryset() method.
    def get_queryset(self):
        """Retrieve recipes for the authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class fo requests"""
        if self.action == "list":
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # Save the new recipe, associating it with the currently authenticated user
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database. Inherits from BaseRecipeAttrViewSet."""

    # Use the TagSerializer to (de)serialize data
    # Use this serializer to convert Tag objects <-> JSON (to JSON) i.e. Use TagSerializer for serialising Tag instances
    serializer_class = serializers.TagSerializer

    # Base queryset of all Tag instances (Contains all instances, will be scoped per-user)
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database. Inherits from BaseRecipeAttrViewSet."""

    # Use the IngredientSerializer to (de)serialize data
    # Convert Ingredient objects <-> JSON (to JSON) i.e. Use IngredientSerializer for serialising Ingredient instances
    serializer_class = serializers.IngredientSerializer

    # Base queryset of all Ingredient instances (Contains all instances, will be scoped per-user)
    queryset = Ingredient.objects.all()
