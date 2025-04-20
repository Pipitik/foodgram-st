from django.core.validators import MinValueValidator
from django.db import models

from constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_MIN_COOKING_TIME,
    RECIPE_INGREDIENT_MIN_AMOUNT,
)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name="Название",
        max_length=INGREDIENT_NAME_MAX_LENGTH
    )

    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit"
            )
        ]
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        verbose_name="Название",
        max_length=RECIPE_NAME_MAX_LENGTH
    )

    text = models.TextField(
        verbose_name="Описание"
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
    )

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[
            MinValueValidator(
                RECIPE_MIN_COOKING_TIME,
                f"Время приготовления не может быть менее "
                f"{RECIPE_MIN_COOKING_TIME} минут(-ы)."
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at",)
        default_related_name = "recipes"

    def __str__(self):
        return f"ID рецепта: {self.id} | {self.name}"


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецептов с ингредиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )

    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(
                RECIPE_INGREDIENT_MIN_AMOUNT,
                "Количество ингредиента должно быть больше нуля!"
            )
        ]
    )

    class Meta:
        verbose_name = "Продукт рецепта"
        verbose_name_plural = "Продукты рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]
        default_related_name = "recipe_ingredients"

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount}"
            f"{self.ingredient.measurement_unit} для {self.recipe.name}"
        )


class BaseUserRecipe(models.Model):
    """Базовый класс для Favorite и ShoppingCart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="%(class)ss"
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="%(class)ss"
    )

    class Meta:
        abstract = True
        ordering = ['user', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="%(app_label)s_%(class)s_unique_user_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"


class Favorite(BaseUserRecipe):
    """Модель избранных рецептов."""

    class Meta(BaseUserRecipe.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class ShoppingCart(BaseUserRecipe):
    """Модель корзины покупок."""

    class Meta(BaseUserRecipe.Meta):
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
