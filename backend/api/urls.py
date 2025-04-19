from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "s/<int:pk>/",
        RecipeViewSet.as_view({"get": "get_link"}),
        name="recipe-short-link",
    ),
]
