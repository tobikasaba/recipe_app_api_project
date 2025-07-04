"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe  # Specify the model to serialise
        # Lists the model fields to include in the serialized representation:
        # The auto-generated primary key id, plus title, preparation time (time_minutes), price and any external link.
        fields = [
            "id",  # Primary key (read-only)
            "title",  # Recipe title
            "time_minutes",  # Preparation time in minutes
            "price",  # Decimal price (e.g. 12.50)
            "link",  # Optional external URL
        ]
        read_only_fields = ["id"]  # PClients cannot set the ID


# Extends RecipeSerializer to include the description field
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        # Inherit model & read_only_fields, then add description
        fields = RecipeSerializer.Meta.fields + ["description"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag  # Specify the Tag model
        fields = [
            "id",  # Auto-generated primary key (read-only)
            "name",  # Name of the tag
        ]
        read_only_fields = ["id"]  # Clients cannot set the ID
