"""
Views for the recipe APIs
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    # Use this serializer to convert Recipe objects <-> JSON (to JSON)
    # serializer_class = serializers.RecipeSerializer
    serializer_class = serializers.RecipeDetailSerializer

    # Base queryset (will be filtered to logged-in user's recipes)
    queryset = Recipe.objects.all()

    # Use token-based authentication i.e Require token-based authentication for access
    authentication_classes = [TokenAuthentication]

    # Only allow access if the user is authenticated
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


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database"""

    # Use this serializer to convert Tag objects <-> JSON (to JSON) i.e. Use TagSerializer for serialising Tag instances
    serializer_class = serializers.TagSerializer

    # Base queryset (will be filtered to logged-in user's tags)
    queryset = Tag.objects.all()

    # Use token-based authentication i.e. Require token-based authentication for access
    authentication_classes = [TokenAuthentication]

    # Only allow access if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
        # Filter tags by the requesting user and order them by name (descending)
