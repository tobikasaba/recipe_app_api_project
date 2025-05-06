"""
Serializers for the USER API View
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


# Serializer for handling user creation and validation
# UserSerializer extends ModelSerializer, a DRF class that auto-generates serializer fields based on a Django model.
# Used to convert between JSON and Django user model instances — especially useful for user creation via API.
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # Meta is an inner class where we define metadata for the serializer.
    class Meta:
        # Use the custom Django user model created
        model = get_user_model()
        # Expose only these fields via the API. The fields a user can change through the API
        fields = ('email', 'password', 'name')
        # Used to provide extra metadata to our serializer
        # Set password to write-only and require a minimum length of 5
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Overrides the default.create() method of the serializer
    # It uses the create_user() method, which automatically hashes the password before saving.
    # This method only gets called when the validation is successful
    def create(self, validated_data):
        """Create and return a user with an encrypted password"""
        # Use the user manager to create a new user with a hashed password
        return get_user_model().objects.create_user(**validated_data)


# This class inherits from serializers.Serializer, which is more manual (unlike ModelSerializer).
# Used to validate raw data
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""

    # Input field for user's email
    email = serializers.CharField()

    # Input field for user's password
    password = serializers.CharField(
        style={'input_type': 'password'},  # Hides input in browsable API
        trim_whitespace=False              # Keeps leading/trailing spaces
    )

    # Used to validate that the data is correct. Called by the view
    def validate(self, attrs):
        """Validate and authenticate the user"""
        # Extract email and password from incoming data
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user using Django's built-in method
        user = authenticate(
            request=self.context.get('request'),  # Passes the request context
            username=email,  # Even though it's email, Django calls it username
            password=password,
        )

        # Raise error if authentication fails (invalid credentials)
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        # Add the authenticated user to the validated data
        # If successful, attach the authenticated user to the validated data and return it.
        attrs['user'] = user
        return attrs
