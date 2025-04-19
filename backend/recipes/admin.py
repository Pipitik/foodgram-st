from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)
    search_fields = ("name", "measurement_unit")


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "get_favorites_count")
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("author", "created_at")
    inlines = [RecipeIngredientInline]

    @admin.display(description="Избранное")
    def get_favorites_count(self, recipe):
        return recipe.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(Favorite, ShoppingCart)
class FavoriteAndShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__email", "recipe__name")
    list_filter = ("user",)
