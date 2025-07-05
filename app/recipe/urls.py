"""
URL mappings for the recipe app
"""

from django.urls import path, include

# DefaultRouter is used with the API view to automatically create routes for options available for the view
from rest_framework.routers import DefaultRouter
from recipe import views

# Instantiate the default router
router = DefaultRouter()

# Register the RecipeViewSet with the router under the URL prefix 'recipes'
# This will create endpoints like /recipes/, /recipes/{id}/, etc.
# This means the recipe viewset will have auto-generated URLS depending on the functionality enabled on the viewset
router.register("recipes", views.RecipeViewSet)

router.register("tags", views.TagViewSet)

app_name = "recipe"

urlpatterns = [
    path("", include(router.urls)),
]
