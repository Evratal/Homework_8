from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from .models import Course, Lesson
from users.models import Subscription


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.admin
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.admin
        )

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('course:lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_video_link(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('course:lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://vimeo.com/test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )

    def test_subscribe(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:subscriptions')
        data = {'course_id': self.course.id}

        # Subscribe
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

        # Unsubscribe
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())


class PaginationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.courses = [Course.objects.create(
            title=f'Course {i}',
            description=f'Description {i}'
        ) for i in range(15)]

    def test_course_pagination(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('course:course-list')
        response = self.client.get(url, {'page': 2, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 15)