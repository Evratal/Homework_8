from django.db import models
from django.core.validators import MinLengthValidator, URLValidator
from django.core.validators import URLValidator
from .validators import validate_youtube_url

class Course(models.Model):
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
        help_text="Введите название курса",
    )
    preview = models.ImageField(
        upload_to="course/courses/previews/",
        verbose_name="Превью курса",
        help_text="Загрузите изображение для курса",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Описание курса", help_text="Добавьте описание курса"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название урока",
        help_text="Введите название урока",
        validators=[MinLengthValidator(5)],
    )
    description = models.TextField(
        verbose_name="Описание урока", help_text="Добавьте описание урока"
    )
    preview = models.ImageField(
        upload_to="course/lessons/previews/",
        verbose_name="Превью урока",
        help_text="Загрузите изображение для урока",
        blank=True,
        null=True,
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
        help_text="Добавьте ссылку на видео",
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
        validators=[URLValidator(), validate_youtube_url],
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
