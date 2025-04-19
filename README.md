# Продуктовый помощник Foodgram 


## Описание проекта Foodgram

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Зарегистрированным пользователям также будет доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии

- Django
- Docker
- Nginx
- React
- GitHub Actions
- Gunicorn
- PostgreSQL

## Запуск проекта

- Приведённые ниже команды следует выполнять в директории infra/.
- При необходимости измените файл .env.

Выполните команду сборки контейнеров:
```bash
docker compose up -d --build
```

- При выполнении следующей команды получаем список запущенных контейнеров:  
```bash
docker container ls
```

### Выполните миграции:
```bash
docker compose exec backend python manage.py migrate
```
### Создайте суперпользователя:
```bash
docker compose exec backend python manage.py createsuperuser
```
### Заполните базу тестовыми данными:
```bash
docker compose exec backend python manage.py load_ingredients data/ingredients.json
```
### Загрузите статику:
```bash
docker compose exec backend python manage.py collectstatic --no-input
```

## Примеры запросов и ответов

### Список рецептов
```
Запрос: GET <URL>/api/recipes/

Ответ:
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "name": "Варёное нечто",
            "text": "Варить 20 минут",
            "image": "http://127.0.0.1:8000/media/recipes/images/81ed441e-74d7-4d4f-89a5-45adda50d049.png",
            "author": {
                "id": 1,
                "username": "vasya.ivanov",
                "email": "vivanov@yandex.ru",
                "first_name": "Вася",
                "last_name": "Иванов",
                "avatar": null,
                "is_subscribed": false
            },
            "cooking_time": 25,
            "ingredients": [
                {
                    "id": 1195,
                    "name": "Панифарин",
                    "measurement_unit": "г",
                    "amount": 20
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 4,
            "name": "Нечто жареное",
            "text": "Жарить 10 минут",
            "image": "http://127.0.0.1:8000/media/recipes/images/f43b3a8c-43dd-48f4-8bf8-2819052513a3.png",
            "author": {
                "id": 2,
                "username": "second-user",
                "email": "second_user@email.org",
                "first_name": "Андрей",
                "last_name": "Макаревский",
                "avatar": null,
                "is_subscribed": false
            },
            "cooking_time": 10,
            "ingredients": [
                {
                    "id": 1195,
                    "name": "Панифарин",
                    "measurement_unit": "г",
                    "amount": 20
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 3,
            "name": "Еда без дополнительной обработки",
            "text": "Просто съесть",
            "image": "http://127.0.0.1:8000/media/recipes/images/81ba9c7a-5e6a-48ac-a2a6-98a1560d47ba.png",
            "author": {
                "id": 2,
                "username": "second-user",
                "email": "second_user@email.org",
                "first_name": "Андрей",
                "last_name": "Макаревский",
                "avatar": null,
                "is_subscribed": false
            },
            "cooking_time": 1,
            "ingredients": [
                {
                    "id": 170,
                    "name": "Буррата",
                    "measurement_unit": "г",
                    "amount": 10
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 2,
            "name": "Еще одна попытка приготовить еду",
            "text": "Вероятно стоит это смешать.",
            "image": "http://127.0.0.1:8000/media/recipes/images/efd270aa-8b60-403d-bfd9-b82448a38623.png",
            "author": {
                "id": 2,
                "username": "second-user",
                "email": "second_user@email.org",
                "first_name": "Андрей",
                "last_name": "Макаревский",
                "avatar": null,
                "is_subscribed": false
            },
            "cooking_time": 10,
            "ingredients": [
                {
                    "id": 170,
                    "name": "Буррата",
                    "measurement_unit": "г",
                    "amount": 10
                },
                {
                    "id": 1195,
                    "name": "Панифарин",
                    "measurement_unit": "г",
                    "amount": 20
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 1,
            "name": "Нечто съедобное (пробовать на свой страх и риск)",
            "text": "Приготовьте как нибудь эти ингредиеты, не забудьте посолить.",
            "image": "http://127.0.0.1:8000/media/recipes/images/5d1ea04f-428c-44bf-b9bc-7326e944d11b.png",
            "author": {
                "id": 2,
                "username": "second-user",
                "email": "second_user@email.org",
                "first_name": "Андрей",
                "last_name": "Макаревский",
                "avatar": null,
                "is_subscribed": false
            },
            "cooking_time": 12,
            "ingredients": [
                {
                    "id": 170,
                    "name": "Буррата",
                    "measurement_unit": "г",
                    "amount": 25
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        }
    ]
}
```

### Подробности рецепта

```
Запрос: GET <URL>/api/recipes/<RecipeID>/

Ответ:
{
    "id": 1,
    "name": "Нечто съедобное (пробовать на свой страх и риск)",
    "text": "Приготовьте как нибудь эти ингредиеты, не забудьте посолить.",
    "image": "http://127.0.0.1:8000/media/recipes/images/5d1ea04f-428c-44bf-b9bc-7326e944d11b.png",
    "author": {
        "id": 2,
        "username": "second-user",
        "email": "second_user@email.org",
        "first_name": "Андрей",
        "last_name": "Макаревский",
        "avatar": null,
        "is_subscribed": false
    },
    "cooking_time": 12,
    "ingredients": [
        {
            "id": 170,
            "name": "Буррата",
            "measurement_unit": "г",
            "amount": 25
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false
}
```

### Подписки

```
Запрос: <URL>/api/users/subscriptions/

Ответ:
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "username": "second-user",
            "email": "second_user@email.org",
            "first_name": "Андрей",
            "last_name": "Макаревский",
            "avatar": null,
            "is_subscribed": true,
            "recipes": [
                {
                    "id": 4,
                    "name": "Нечто жареное",
                    "image": "/media/recipes/images/f43b3a8c-43dd-48f4-8bf8-2819052513a3.png",
                    "cooking_time": 10
                },
                {
                    "id": 3,
                    "name": "Еда без дополнительной обработки",
                    "image": "/media/recipes/images/81ba9c7a-5e6a-48ac-a2a6-98a1560d47ba.png",
                    "cooking_time": 1
                },
                {
                    "id": 2,
                    "name": "Еще одна попытка приготовить еду",
                    "image": "/media/recipes/images/efd270aa-8b60-403d-bfd9-b82448a38623.png",
                    "cooking_time": 10
                },
                {
                    "id": 1,
                    "name": "Нечто съедобное (пробовать на свой страх и риск)",
                    "image": "/media/recipes/images/5d1ea04f-428c-44bf-b9bc-7326e944d11b.png",
                    "cooking_time": 12
                }
            ],
            "recipes_count": 4
        },
        {
            "id": 3,
            "username": "third-user-username",
            "email": "third-user@user.ru",
            "first_name": "Гордон",
            "last_name": "Рамзиков",
            "avatar": null,
            "is_subscribed": true,
            "recipes": [],
            "recipes_count": 0
        }
    ]
}
```

# Автор

Брюханов Константин