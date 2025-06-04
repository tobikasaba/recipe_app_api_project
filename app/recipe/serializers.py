"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


# Extends RecipeSerializer to add more detailed fields (used in recipe detail views)
# Avoids code duplication and leverages existing logic in RecipeSerializer
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    # Inherit Meta from RecipeSerializer and add the 'description' field
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
