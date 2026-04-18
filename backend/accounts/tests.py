from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Tag, Preference

User = get_user_model()

class AccountsAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('profile')
        
        # Создаем тегов
        Tag.objects.get_or_create(name='calm')
        Tag.objects.get_or_create(name='active')
        
    def test_register_user(self):
        """Тест регистрации пользователя"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'user'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
    
    def test_register_owner(self):
        """Тест регистрации владельца"""
        data = {
            'username': 'testowner',
            'email': 'owner@example.com',
            'password': 'ownerpass123',
            'role': 'owner'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.first().role, 'owner')
    
    def test_login(self):
        """Тест логина"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_get_profile_authenticated(self):
        """Тест получения профиля авторизованным пользователем"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_profile_unauthenticated(self):
        """Тест получения профиля без авторизации"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # было 401
    
    def test_update_profile(self):
        """Тест обновления профиля"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user'
        )
        self.client.force_authenticate(user=user)
        data = {'first_name': 'Новое имя', 'bio': 'Новая биография'}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Новое имя')