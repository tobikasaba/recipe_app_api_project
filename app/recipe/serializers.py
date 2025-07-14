"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    # Configures the serializer’s behaviour
    class Meta:
        # Specify the Django model to serialize
        model = Ingredient

        # Only include the id and name fields in the API
        fields = ["id", "name"]

        # Prevent clients from providing or modifying the id
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        # Specify the Tag model
        model = Tag

        fields = [
            "id",  # Auto-generated primary key (read-only)
            "name",  # Name of the tag
        ]
        read_only_fields = ["id"]  # Clients cannot set the ID


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipes

    Convention treats methods whose names begin with a single underscore (example, _get_or_create_tags) as “private”.
    They aren’t part of the class’s public API and aren’t intended to be used outside the class,
    even though Python doesn’t enforce true access restrictions.
    """

    # making TagSerializer & IngredientSerializer a nesteds serializers for Recipe Serializer
    # a list of tags and ingredients will be assigned to a recipe
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        # Specify the model to serialize
        model = Recipe

        # Lists the model fields to include in the serialized representation:
        # The auto generated primary key id, plus title, preparation time (time_minutes), price and any external link.
        fields = [
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",  # Nested tags list
            "ingredients",  # Nested ingredients list
        ]

        # Clients cannot set the ID
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        # Get the authenticated user from the request context
        auth_user = self.context["request"].user

        # Iterate over each tag dict (e.g. {"name": "Thai"})
        for tag in tags:
            # Fetch or create a Tag for this user and tag data
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,  # Ensure the tag is linked to the current user
                **tag  # Unpacks the dict into keyword arguments, equivalent to writing name="Thai".
            )
            # Link each tag object to the provided recipe
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed"""
        # Get the authenticated user from the request context
        auth_user = self.context["request"].user

        for ingredient in ingredients:
            # Fetch or create an Ingredient for this user and tag data
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,  # Ensure the ingredient is linked to the current user
                **ingredient  # Unpacks the dict into keyword arguments, equivalent to writing name="Salt".
            )
            # Link each ingredient object to the provided recipe
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe"""
        # Extract 'tags' from the validated data so it doesn't get passed to Recipe.objects.create()
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        # Create a new Recipe instance with the remaining validated data
        recipe = Recipe.objects.create(**validated_data)

        # Handle the creation or association of tags
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        # Return the created recipe instance
        return recipe

    def update(self, recipe_instance, validated_data):
        """Update recipe"""

        # Extract and remove the 'tags' & 'ingredients' fields from the validated data if present
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)

        # If tags are included in the request, clear old tags and assign new ones
        if tags is not None:
            recipe_instance.tags.clear()  # Remove all current tags from the recipe
            self._get_or_create_tags(tags, recipe_instance)  # Add new or existing tags

        # If ingredients are included in the request, clear old ingredients and assign new ones
        if ingredients is not None:
            recipe_instance.ingredients.clear()  # Remove all current ingredients from the recipe
            self._get_or_create_ingredients(
                ingredients, recipe_instance
            )  # Add new or existing ingredients

        # Set the remaining fields (e.g., title, time_minutes) on the instance
        for attr, value in validated_data.items():
            setattr(recipe_instance, attr, value)

        # Save the updated recipe object to the database
        recipe_instance.save()

        # Return the updated instance
        return recipe_instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for recipe detail view
    Extends RecipeSerializer to include the description field
    """

    class Meta(RecipeSerializer.Meta):
        # Inherit model & read_only_fields, then add description
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images to recipe

    A new API is created because it’s best practice to upload one type of data to an API:
    - Recipe data via form fields
    - Image data via file upload
    """

    class Meta:
        # Specify the Django model this serializer works with
        model = Recipe
        # Only expose the recipe's id and its image field
        fields = ["id", "image"]
        # Prevent clients from providing or modifying the id
        read_only_fields = ["id"]
        # Require that an image file be included
        extra_kwargs = {"image": {"required": True}}
