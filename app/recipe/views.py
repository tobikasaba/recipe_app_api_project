"""
Views for the recipe APIs
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    # Use this serializer to convert Recipe objects <-> JSON
    serializer_class = serializers.RecipeSerializer

    # Base queryset (will be filtered to logged-in user's recipes)
    queryset = Recipe.objects.all()

    # Use token-based authentication
    authentication_classes = [TokenAuthentication]

    # Only allow access if the user is authenticated
    permission_classes = [IsAuthenticated]

    # Overrides the default get_queryset() method.
    def get_queryset(self):
        """Retrieve recipes for the authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

