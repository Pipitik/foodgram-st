from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "password",
    )
    search_fields = ("username", "email")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("follower", "author")
    search_fields = ("follower__email", "author__email")
