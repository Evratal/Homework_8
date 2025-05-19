# Платформа онлайн-курсов (Django + Celery + Stripe)


Система управления образовательными курсами с подписками, платежами и автоматическими уведомлениями.

##  Основные функции

- Создание и управление курсами/уроками
- Подписка на обновления курсов
- Интеграция с Stripe для онлайн-платежей
- Асинхронная рассылка email-уведомлений
- Периодические задачи через Celery Beat
- Автоматическая блокировка неактивных пользователей

##  Быстрый старт

### Предварительные требования
- Python 3.8+
- Poetry (для управления зависимостями)
- Redis (для Celery)
- Stripe аккаунт (тестовый режим)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-репозиторий.git
cd project
```


2.Установите зависимости через Poetry:
```bash
poetry install
```
3. Настройте окружение (создайте .env файл):
```bash
SECRET_KEY=ваш-secret-key
DEBUG=True
STRIPE_API_KEY=sk_test_ваш-ключ
REDIS_URL=redis://localhost:6379/0
```

4. Примените миграции:
```bash
poetry run python manage.py migrate
```

5. Создайте администратора:
```bash
poetry run python manage.py createsuperuser
```

##  Запуск проекта

### Основной сервер:
```bash
poetry run python manage.py runserver
```

### Celery Worker:
```bash
poetry run celery -A config worker -l INFO
```

### Celery Beat (периодические задачи):
```bash
poetry run celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

##  Основные API-эндпоинты

Эндпоинт	                Описание
GET /api/courses/	        Список курсов с пагинацией
POST /api/subscriptions/	Подписка/отписка от курса
POST /api/payments/	        Создание платежа через Stripe
GET /api/lessons/	        Список уроков с фильтрацией


