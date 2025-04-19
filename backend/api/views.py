from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.utils import timezone
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import RecipeFilter
from .pagination import PagesPagination
from .permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
)
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribedUserSerializer,
    SubscriptionSerializer,
    UserSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from users.models import Subscription, User


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagesPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated]
    )
    def get_me(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def change_avatar(self, request):
        user = request.user
        if request.method == "PUT":
            if "avatar" not in request.data:
                return Response(
                    {"detail": "Это поле обязательно"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": serializer.data["avatar"]},
                status=status.HTTP_200_OK
            )
        user.avatar.delete()
        user.save()
        return Response(
            {"message": "Аватар успешно удалён"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
           detail=True,
           methods=["post", "delete"],
           url_path="subscribe"
       )
    def subscribe_and_unsubscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if request.method == "POST":
            serializer = SubscriptionSerializer(
                data={"author": author.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            subscription = serializer.save(follower=request.user)
            return Response(serializer.to_representation(subscription), status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(follower=request.user, author=author).first()
        if not subscription:
            return Response(
                {"detail": "Подписка не существует."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=["get"], url_path="subscriptions")
    def subscriptions(self, request):
        subscriptions = (
            User.objects.filter(author__follower=request.user)
        )

        paginated_subscriptions = self.paginate_queryset(subscriptions)

        serializer = SubscribedUserSerializer( 
            paginated_subscriptions, 
            many=True, 
            context={'request': request} 
        ) 

        return self.get_paginated_response(serializer.data) 



class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PagesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    @staticmethod
    def _toggle_favorite_or_shopping_cart(request, recipe, model):
        serializer_class = (
            FavoriteSerializer if model == Favorite else ShoppingCartSerializer
        )

        if request.method == "POST":
            serializer = serializer_class(
                data={"recipe": recipe.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=request.user)
            return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)

        instance_item = model.objects.filter(
            user=request.user, 
            recipe=recipe 
        ).first()

        if not instance_item: 
            return Response( 
                {"detail": "Рецепт отсутствует"}, 
                status=status.HTTP_400_BAD_REQUEST 
            )

        instance_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def change_favorited_recipes(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._toggle_favorite_or_shopping_cart(request, recipe, Favorite)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart"
    )
    def change_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._toggle_favorite_or_shopping_cart(request, recipe, ShoppingCart)

    @staticmethod
    def _prepare_text(request, ingredients):
        today = timezone.now().strftime("%d.%m.%Y")
        report_lines = [
            f"Список покупок на {today}:",
            "Продукты:",
        ]

        for idx, item in enumerate(ingredients, start=1):
            name = item["ingredient_name"].capitalize()
            unit = item["measurement_unit"]
            amount = item["total_amount"]
            report_lines.append(f"{idx}. {name} ({unit}) - {amount}")

        recipe_names = request.user.shoppingcarts.values_list(
            "recipe__name", flat=True
        ).distinct().order_by("recipe__name")
        report_lines.append("\nРецепты, для которых нужны эти продукты:")
        for idx, recipe in enumerate(recipe_names, start=1):
            report_lines.append(f"{idx}. {recipe}")

        return "\n".join(report_lines)

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            ingredient_name=F("ingredient__name"),
            measurement_unit=F("ingredient__measurement_unit")
        ).annotate(
            total_amount=Sum("amount")
        ).order_by("ingredient__name")

        report_text = self._prepare_text(request, ingredients)
        return FileResponse(
            report_text,
            content_type="text/plain",
            filename="shopping_cart.txt"
        )

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        short_link = request.build_absolute_uri(
            reverse("recipe-short-link", args=[pk])
        )
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)
