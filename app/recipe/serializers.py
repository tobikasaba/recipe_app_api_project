"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag


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
    """Serializer for recipes"""

    # making TagSerializer a nested serializer for Recipe Serializer
    # a list of tags will be assigned to a recipe
    tags = TagSerializer(many=True, required=False)

    class Meta:
        # Specify the model to serialize
        model = Recipe

        # Lists the model fields to include in the serialized representation:
        # The auto generated primary key id, plus title, preparation time (time_minutes), price and any external link.
        fields = [
            "id",  # Primary key (read-only)
            "title",  # Recipe title
            "time_minutes",  # Preparation time in minutes
            "price",  # Decimal price (e.g. 12.50)
            "link",  # Optional external URL
            "tags",  # Nested tags list
        ]
        # Clients cannot set the ID
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Create a recipe"""
        # Extract any nested tags so they don’t get passed to Recipe.objects.create()
        tags = validated_data.pop("tags", [])
        # Create a recipe with the rest of the validated data
        recipe = Recipe.objects.create(**validated_data)
        # Get the authenticated user from context
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,  # Ensure the recipe is linked to the current user
                **tag,  # Unpacks the tag’s own fields e.g. name="Thai"
            )
            # Link each tag to the new recipe
            recipe.tags.add(tag_obj)

        return recipe


# Extends RecipeSerializer to include the description field
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        # Inherit model & read_only_fields, then add description
        fields = RecipeSerializer.Meta.fields + ["description"]
