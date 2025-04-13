from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователей"""

    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
        max_length=254
    )

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@_-]+$',
                message=(
                    'Username должен содержать только буквы, '
                    'цифры и символы @._-'
                )
            )
        ]
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=255,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=255,
        blank=False,
        null=False
    )

    avatar = models.ImageField(
        verbose_name="Аватар пользователя",
        upload_to='avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Модель подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
