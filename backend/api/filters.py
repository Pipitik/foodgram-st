from django_filters import FilterSet, NumberFilter, BooleanFilter

from recipes.models import Recipe

class RecipeFilter(FilterSet):
    author_id = NumberFilter(field_name="author__id")
    is_favorited = NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = NumberFilter(method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset
