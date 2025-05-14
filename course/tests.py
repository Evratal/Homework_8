from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from .models import Course, Lesson
from users.models import Subscription


class LessonTestCase(APITestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            password='modpass123'
        )
        self.moderator.groups.create(name='moderators')  # Назначаем модератором
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

        # Создаем тестовый курс и урок
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

        # URL для тестирования
        self.list_url = reverse('course:lesson-list')
        self.detail_url = reverse('course:lesson-detail', args=[self.lesson.id])

    # --- CREATE TESTS (существующие тесты) ---
    def test_lesson_create(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=test'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_invalid_video_link(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://vimeo.com/test'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- LIST TESTS ---
    def test_lesson_list_admin(self):
        """Админ видит все уроки"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_lesson_list_moderator(self):
        """Модератор видит все уроки"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_lesson_list_user(self):
        """Обычный пользователь видит только свои уроки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # У пользователя нет уроков

    # --- RETRIEVE TESTS ---
    def test_lesson_retrieve_admin(self):
        """Админ может просмотреть любой урок"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Lesson')

    def test_lesson_retrieve_moderator(self):
        """Модератор может просмотреть любой урок"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_retrieve_user_forbidden(self):
        """Обычный пользователь не может просмотреть чужой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- UPDATE TESTS ---
    def test_lesson_update_admin(self):
        """Админ может обновить урок"""
        self.client.force_authenticate(user=self.admin)
        data = {'title': 'Updated Lesson Title'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_lesson_update_moderator(self):
        """Модератор может обновить урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {'description': 'Updated by moderator'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_user_forbidden(self):
        """Обычный пользователь не может обновить чужой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, {'title': 'Try to update'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- DESTROY TESTS ---
    def test_lesson_destroy_admin(self):
        """Админ может удалить урок"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_lesson_destroy_moderator_forbidden(self):
        """Модератор может удалить урок"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_destroy_user_forbidden(self):
        """Обычный пользователь не может удалить чужой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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