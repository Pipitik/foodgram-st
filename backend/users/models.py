from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX_VALIDATOR,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
)


class User(AbstractUser):
    """Модель пользователей."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
        "password"
    ]

    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
        max_length=EMAIL_MAX_LENGTH
    )

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX_VALIDATOR,
                message=(
                    "Username должен содержать только буквы, "
                    "цифры и символы [.@+-]."
                )
            )
        ]
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=FIRST_NAME_MAX_LENGTH
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=LAST_NAME_MAX_LENGTH
    )

    avatar = models.ImageField(
        verbose_name="Аватар пользователя",
        upload_to='avatars/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Модель подписки на авторов."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "author"],
                name="unique_subscription"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("follower",)

    def __str__(self):
        return f"{self.follower} подписан на {self.author}"
