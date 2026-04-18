from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from animals.models import Animal, Characteristic
from accounts.models import Tag, Preference

User = get_user_model()

class AnimalsAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.swipe_url = reverse('swipe-animals')
        self.my_animals_url = reverse('my-animals')
        
        # Создаем пользователей
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='owner123',
            role='owner'
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123',
            role='user'
        )
        
        # Создаем теги
        self.tag_calm = Tag.objects.create(name='calm')
        self.tag_active = Tag.objects.create(name='active')
        
        # Создаем животных
        self.animal1 = Animal.objects.create(
            owner=self.owner,
            name='Барсик',
            years_of_age=2,
            description='Спокойный кот'
        )
        Characteristic.objects.create(pet=self.animal1, character='calm')
        
        self.animal2 = Animal.objects.create(
            owner=self.owner,
            name='Рекс',
            years_of_age=3,
            description='Активный пес'
        )
        Characteristic.objects.create(pet=self.animal2, character='active')
    
    def test_swipe_animals_authenticated(self):
        """Тест получения списка животных для свайпа (авторизован)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.swipe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_swipe_animals_unauthenticated(self):
        """Тест получения списка животных без авторизации"""
        response = self.client.get(self.swipe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_swipe_excludes_own_animals(self):
        """Тест: пользователь не видит своих животных"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.swipe_url)
        self.assertEqual(len(response.data), 0)
    
    def test_owner_animals_list(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.my_animals_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        names = [item['name'] for item in response.data]
        self.assertIn('Барсик', names)
        self.assertIn('Рекс', names)
    
    def test_non_owner_cannot_get_animals_list(self):
        """Тест: обычный пользователь не получает список животных владельца"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_animals_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_animal(self):
        """Тест создания животного владельцем"""
        self.client.force_authenticate(user=self.owner)
        create_url = reverse('create-animal')
        data = {
            'name': 'Новый питомец',
            'years_of_age': 1,
            'description': 'Описание',
            'photo': 'http://example.com/photo.jpg'
        }
        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Animal.objects.count(), 3)
    
    def test_update_animal(self):
        """Тест обновления животного"""
        self.client.force_authenticate(user=self.owner)
        detail_url = reverse('my-animal-detail', args=[self.animal1.id])
        data = {'name': 'Новое имя'}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.animal1.refresh_from_db()
        self.assertEqual(self.animal1.name, 'Новое имя')
    
    def test_delete_animal(self):
        """Тест удаления животного"""
        self.client.force_authenticate(user=self.owner)
        detail_url = reverse('my-animal-detail', args=[self.animal1.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Animal.objects.count(), 1)