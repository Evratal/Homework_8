from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsOwner
from .paginators import LessonPaginator, CoursePaginator
from .tasks import send_course_update_notification
from datetime import datetime, timedelta


# Для курсов (ViewSets)
class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = CoursePaginator
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        # Проверка на 4 часа (доп. задание)
        now = datetime.now(instance.updated_at.tzinfo)
        if now - instance.updated_at > timedelta(hours=4):
            send_course_update_notification.delay(instance.id)

# Для уроков (Generic-классы)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = LessonPaginator
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = Lesson.objects.all()
        course_id = self.kwargs.get('course_id')

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if not self.request.user.groups.filter(name='moderators').exists():
            queryset = queryset.filter(owner=self.request.user)

        return queryset

class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)
