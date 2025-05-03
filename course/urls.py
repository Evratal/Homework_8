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
