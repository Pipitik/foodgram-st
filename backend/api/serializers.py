from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from constants import RECIPE_INGREDIENT_MIN_AMOUNT
from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
)
from users.models import Subscription, User


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, user):
        request_user = self.context["request"].user
        return request_user.is_authenticated and Subscription.objects.filter(
            author=user,
            follower=request_user
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient.id"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField(min_value=RECIPE_INGREDIENT_MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients", many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "image",
            "author",
            "cooking_time",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, data):
        if not data.get("recipe_ingredients"):
            raise serializers.ValidationError({
                "detail": 'Поле "ingredients" не может быть пустым.'
            })
        
        ingredients = data["recipe_ingredients"]
        if not isinstance(ingredients, list):
            raise serializers.ValidationError({
                "detail": 'Поле "ingredients" должно быть списком.'
            })

        ingredient_ids = [ingredient["ingredient"]["id"] for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError({
                "detail": "Ингредиенты не должны повторяться."
            })

        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError({
                "detail": 'Поле "image" не может быть пустым.'
            })
        return image

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        validated_data["author"] = self.context.get("request").user
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient["ingredient"]["id"],
                amount=ingredient["amount"]
            )
            for ingredient in ingredients_data
        )

    def _check_existence(self, model, recipe):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()
        )

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def get_is_favorited(self, recipe):
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_existence(ShoppingCart, recipe)

    def to_representation(self, instance):
        return super().to_representation(instance)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribedUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source="recipes.count",
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, author):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        if not recipes_limit:
            recipes = author.recipes.all()
        else:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise ValidationError({
                    "detail": 'Параметр "recipes_limit" должен быть целым числом.'
                })

            if recipes_limit < 1:
                raise ValidationError({
                    "detail": 'Параметр "recipes_limit" должен быть больше 0.'
                })

            recipes = author.recipes.all()[:recipes_limit]

        return ShortRecipeSerializer(recipes, many=True).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("follower", "author")
        read_only_fields = ("follower",)

    def validate(self, data):
        if not data.get("author"):
            raise serializers.ValidationError(
                {"detail": 'Поле "author" не может быть пустым.'}
            )

        request = self.context.get("request")
        author = data["author"]
        if author == request.user:
            raise serializers.ValidationError(
                {"detail": "Нельзя подписаться на самого себя."}
            )

        if Subscription.objects.filter(follower=request.user, author=author).exists():
            raise serializers.ValidationError(
                {"detail": "Подписка уже была оформлена."}
            )

        return data

    def to_representation(self, instance):
        author = instance.author
        recipes_limit = self.context["request"].query_params.get("recipes_limit")
        recipes = author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return {
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            "email": author.email,
            "is_subscribed": True,
            "avatar": author.avatar.url if author.avatar else None,
            "recipes_count": author.recipes.count(),
            "recipes": ShortRecipeSerializer(recipes, many=True).data,
        }


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        read_only_fields = ("user",)

    def validate(self, data):
        if not data.get("recipe"):
            raise serializers.ValidationError(
                {"detail": 'Поле "recipe" не может быть пустым.'}
            )

        user = self.context["request"].user
        recipe = data["recipe"]
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"detail": "Рецепт уже добавлен в избранное."}
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        read_only_fields = ("user",)

    def validate(self, data):
        if not data.get("recipe"):
            raise serializers.ValidationError(
                {"detail": 'Поле "recipe" не может быть пустым.'}
            )

        user = self.context["request"].user
        recipe = data["recipe"]
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"detail": "Рецепт уже добавлен в корзину."}
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data
