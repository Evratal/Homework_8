from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import Subscription
from datetime import datetime, timedelta


@shared_task
def send_course_update_notification(course_id):
    from course.models import Course
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course)

    for subscription in subscriptions:
        send_mail(
            f'Обновление курса {course.title}',
            f'Курс {course.title} был обновлен. Посмотрите новые материалы!',
            settings.EMAIL_HOST_USER,
            [subscription.user.email],
            fail_silently=False,
        )


@shared_task
def check_inactive_users():
    from django.contrib.auth.models import User
    from django.utils import timezone

    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True
    )

    for user in inactive_users:
        user.is_active = False
        user.save()

