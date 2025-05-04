"""
Views for the user API
"""
from rest_framework import generics
from serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """API view to create a new user in the system"""

    # Specifies that the UserSerializer should be used to validate and save the incoming request data (new users).
    serializer_class = UserSerializer
