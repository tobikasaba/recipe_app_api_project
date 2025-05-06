"""
Views for the user API
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """API view to create a new user in the system"""

    # Specifies that the UserSerializer should be used to validate and save the incoming request data (new users).
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user (via email and password)"""

    # Use AuthTokenSerializer custom serializer that authenticates via email/password
    serializer_class = AuthTokenSerializer

    # Enable the browsable API renderer (useful for UI testing)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
