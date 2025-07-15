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

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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


# Enhance the generated OpenAPI docs for the list endpoint
# @extend_schema_view is a decorator from drf-spectacular that customises OpenAPI docs for specific viewset actions.
@extend_schema_view(
    # Applies this schema override to the list action (i.e. GET /recipes/).
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",  # query param name
                OpenApiTypes.STR,  # type = string
                description="Comma separated list of tags IDs to filter",  # help text
            ),
            OpenApiParameter(
                "ingredients",  # query param name
                OpenApiTypes.STR,  # type = string
                description="Comma separated list of ingredient IDs to filter",  # help text
            ),
        ]
    )
)
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

    def _params_to_ints(self, qs):
        """Covert a list of string IDs to a list of integers"""

        # Take the incoming comma-separated string of IDs (qs),
        # split it on each comma,
        # convert each substring to an integer,
        # and return the list of integers for filtering.
        return [int(str_id) for str_id in qs.split(",")]

    # Overrides the default get_queryset() method.
    # Override the base queryset to support optional filtering
    def get_queryset(self):
        """Retrieve recipes for the authenticated user only"""

        # Read optional comma-separated filter params from the UR
        # request.query_params is a dictionary-like object containing all the URL’s “query string” parameters
        # everything after the '?' in the path.
        # E.g. for tags, /api/recipes/?tags=1,2&search=curry => "1, 2"
        # e.g. for search, /api/recipes/?tags=1,2&search=curry => "curry"
        # the grabs the IDs of tags and ingredients intended to be filtered
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")

        # Start from all recipes defined on this viewset
        queryset = self.queryset

        # If tag IDs were provided, convert and filter by those tags
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)

        # If ingredient IDs were provided, convert and filter by those ingredients
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        # Finally, scope to this user, order by most-recent, and remove duplicates
        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Return the serializer class fo requests"""
        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # Save the new recipe, associating it with the currently authenticated user
        serializer.save(user=self.request.user)

    # Add a custom POST endpoint at /recipes/{pk}/upload-image/
    @action(
        methods=["POST"],  # Only allow POST requests here
        detail=True,  # This is for a single recipe, not the whole list
        url_path="upload-image",  # The URL suffix to use after the recipe’s ID
    )
    def upload_image(self, request, pk=None):
        """

        In Django REST Framework, viewsets give you standard endpoints like
        list (GET /recipes/) and detail (GET /recipes/123/).
        The @action decorator lets you add your own extra endpoints to a viewset without writing a brand-new view.
        Think of it as “pinning on” a custom button to each recipe (or to the whole list)
        that does something special beyond the usual CRUD.

        Upload an image to a specific recipe.
        - `request` contains the uploaded file in request.data/files.
        - `pk` is the recipe’s primary key from the URL (e.g., 123).
        """
        # Fetch the target recipe instance (or 404 if not found)
        recipe = self.get_object()

        # Bind the incoming file data to our image-only serializer
        serializer = self.get_serializer(recipe, data=request.data)

        # If the file is valid, save it and return the updated recipe data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Otherwise return the validation errors with a 400 status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
