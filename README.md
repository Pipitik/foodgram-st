# Продуктовый помощник Foodgram 

## Описание проекта Foodgram

Из задания: Вам предстоит поработать с проектом «Фудграм» — сайтом, на котором
пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. Зарегистрированным пользователям
также будет доступен сервис «Список покупок». Он позволит создавать список
продуктов, которые нужно купить для приготовления выбранных блюд.

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
