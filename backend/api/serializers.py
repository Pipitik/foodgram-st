from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
)
from rest_framework import serializers
from users.models import Subscription, User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, user):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=user.id,
            user=request_user.id
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'author',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError({
                'details': 'Поле `image` не может быть пустым'
            })
        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения'
            })
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле `ingredients` не может быть пустым.'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле `ingredients` не может быть пустым.'
            )
        
        # Проверка на дублирующиеся ингредиенты
        unique_ingredients = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            unique_ingredients.add(ingredient_id)
        
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения'
            })
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения'
            })
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        )

    def _check_existence(self, model, recipe):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists()
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ''

    def get_is_favorited(self, recipe):
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_existence(ShoppingCart, recipe)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
)
from rest_framework import serializers
from users.models import Subscription, User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=user.id,
            user=request_user.id,
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'author',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError({
                'details': 'Поле `image` не может быть пустым',
            })
        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле `ingredients` не может быть пустым.',
            )

        unique_ingredients = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.',
                )
            unique_ingredients.add(ingredient_id)

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        )

    def _check_existence(self, model, recipe):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists()
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ''

    def get_is_favorited(self, recipe):
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_existence(ShoppingCart, recipe)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
)
from rest_framework import serializers
from users.models import Subscription, User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=user.id,
            user=request_user.id,
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'author',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError({
                'details': 'Поле `image` не может быть пустым',
            })
        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле `ingredients` не может быть пустым.',
            )

        unique_ingredients = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.',
                )
            unique_ingredients.add(ingredient_id)

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'details': 'Поле `ingredients` обязательно для заполнения',
            })
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        )

    def _check_existence(self, model, recipe):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists()
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ''

    def get_is_favorited(self, recipe):
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_existence(ShoppingCart, recipe)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribedUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='recipes.count',
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit and int(recipes_limit) < 1:
            raise ValidationError(
                'Параметр `recipes_limit` должен быть больше 0.',
            )
        recipes = author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data
