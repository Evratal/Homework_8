# Приложение cours

# course/apps
from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "course"


# course/models
from django.db import models
from django.core.validators import MinLengthValidator, URLValidator


class Course(models.Model):
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

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# course/serializers
from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "created_at",
            "updated_at",
            "lessons",
            "lessons_count",
        ]


# course/urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import app_name

from .apps import CourseConfig
from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
)

app_name = CourseConfig.name

router = DefaultRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
]

urlpatterns += router.urls

# course/views
from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


# Для курсов (ViewSets)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


# Для уроков (Generic-классы)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
