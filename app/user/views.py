"""
Views for the user API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """API view to create a new user in the system"""

    # Specifies the serializer to handle input validation and user creation
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user (via email and password)"""

    # Custom serializer that authenticates users using email/password
    serializer_class = AuthTokenSerializer

    # Allows this view to use the browsable API (for easier testing/debugging)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    # Uses the user serializer to retrieve/update user info
    serializer_class = UserSerializer

    # Enforces that the user must be authenticated via a token
    authentication_classes = (authentication.TokenAuthentication,)

    # Ensures only logged-in users can access this endpoint
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the authenticated user"""
        # Instead of using a lookup, we just return the current user
        return self.request.user
