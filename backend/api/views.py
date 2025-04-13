from django.http import FileResponse
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
)
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
from users.models import Subscription, User

from .pagination import PagesPagination
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribedUserSerializer,
    UserSerializer
)

from .permissions import IsAuthorOrReadOnly

class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagesPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def get_me(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def change_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'details': 'Это поле обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                user, data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )
        user.avatar.delete()
        user.save()
        return Response(
            {'message': 'Аватар успешно удалён'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
           detail=True,
           methods=['post', 'delete'],
           url_path='subscribe'
       )
    def subscribe_and_unsubscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            raise ValidationError(
                {'details': 'Нельзя подписаться на самого себя'}
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )

            if not created:
                raise ValidationError({'details': 'Подписка уже была оформлена'})

            recipes_limit = request.query_params.get('recipes_limit')
            recipes = author.recipes.all()
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]

            recipes_data = [
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image.url if recipe.image else None,
                    "cooking_time": recipe.cooking_time
                }
                for recipe in recipes
            ]

            return Response(
                {
                    "id": author.id,
                    "username": author.username,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "email": author.email,
                    "is_subscribed": True,
                    "avatar": author.avatar.url if author.avatar else None,
                    "recipes_count": author.recipes.count(),
                    "recipes": recipes_data
                },
                status=status.HTTP_201_CREATED
            )

        # Проверка на существование подписки перед удалением
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        ).first()

        if not subscription:
            return Response(
                {'details': 'Подписка не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        subscriptions = (
            user.users.all()
            .select_related('author')
        )

        # Пагинация
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('limit', 6)  # Установим значение limit
        paginated_subscriptions = paginator.paginate_queryset(
            subscriptions,
            request
        )

        authors = [
            subscription.author for subscription in paginated_subscriptions
        ]

        serializer = SubscribedUserSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)



class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Метод для получения ингредиентов по имени"""
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PagesPagination


    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        if is_favorited == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)
        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(
                shoppingcarts__user=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def _toggle_favorite_or_shopping_cart(request, recipe, model):
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                raise ValidationError({'details': 'Рецепт уже добавлен'})

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(
            model,
            user=request.user,
            recipe=recipe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def change_favorited_recipes(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            obj, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                raise ValidationError({'details': 'Рецепт уже добавлен в избранное'})

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        # Проверка на существование рецепта в избранном перед удалением
        favorite_item = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()

        if not favorite_item:
            return Response(
                {'details': 'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart'
    )
    def change_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                raise ValidationError({'details': 'Рецепт уже добавлен в корзину'})

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        # Проверка на существование рецепта в корзине перед удалением
        shopping_cart_item = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()

        if not shopping_cart_item:
            return Response(
                {'details': 'Рецепт отсутствует в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        ingredient_totals = {}
        recipe_names = set()

        for item in (request.user.shoppingcarts.all()
                .select_related('recipe')):
            recipe_names.add(item.recipe.name)
            for ingredient_in_recipe in item.recipe.recipe_ingredients.all():
                key = (
                    ingredient_in_recipe.ingredient.name,
                    ingredient_in_recipe.ingredient.measurement_unit
                )
                ingredient_totals[key] = (ingredient_totals.get(key, 0)
                                          + ingredient_in_recipe.amount)

        today = timezone.now().strftime('%d.%m.%Y')
        report_lines = [
            f'Список покупок на {today}:',
            'Продукты:',
        ]

        '''Нумерация и сортировка ингредиентов по имени'''
        for number_of_product, ((name, unit), amount) in enumerate(
            sorted(ingredient_totals.items(), key=lambda x: x[0])
        ):
            report_lines.append(
                f'{number_of_product + 1}. '
                f'{name.capitalize()} ({unit}) - {amount}'
            )

        report_lines.append('\nРецепты, для которых нужны эти продукты:')
        for number_of_product, recipe_name in enumerate(sorted(recipe_names)):
            report_lines.append(f'{number_of_product + 1}. {recipe_name}')

        report_text = '\n'.join(report_lines)

        return FileResponse(
            report_text,
            content_type='text/plain',
            filename='shopping_cart.txt'
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Метод для получения короткой ссылки на рецепт"""
        short_link = request.build_absolute_uri(
            reverse('recipe-short-link', args=[pk])
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
