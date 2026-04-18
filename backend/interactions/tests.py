from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from animals.models import Animal, Characteristic
from interactions.models import Interaction, Match

User = get_user_model()

class InteractionsAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.like_url = reverse('like')
        
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
        
        # Создаем животное
        self.animal = Animal.objects.create(
            owner=self.owner,
            name='Барсик',
            years_of_age=2,
            description='Спокойный кот'
        )
    
    def test_create_like(self):
        """Тест создания лайка"""
        self.client.force_authenticate(user=self.user)
        data = {'animal_id': self.animal.id}
        response = self.client.post(self.like_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Interaction.objects.filter(user=self.user, animal=self.animal).exists())
        self.assertTrue(Match.objects.filter(user=self.user, animal=self.animal).exists())
    
    def test_cannot_like_own_animal(self):
        """Тест: нельзя лайкнуть свое животное"""
        self.client.force_authenticate(user=self.owner)
        data = {'animal_id': self.animal.id}
        response = self.client.post(self.like_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_like_twice(self):
        """Тест: нельзя лайкнуть дважды"""
        self.client.force_authenticate(user=self.user)
        data = {'animal_id': self.animal.id}
        self.client.post(self.like_url, data)
        response = self.client.post(self.like_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_accept_match(self):
        """Тест подтверждения мэтча владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {'animal_id': self.animal.id}
        like_response = self.client.post(self.like_url, data)
        match_id = like_response.data['match_id']
        
        self.client.force_authenticate(user=self.owner)
        accept_url = reverse('accept-match', args=[match_id])
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        match = Match.objects.get(id=match_id)
        self.assertEqual(match.status, 'matched')
    
    def test_get_pending_matches(self):
        """Тест получения ожидающих мэтчей для владельца"""
        # Создаем лайк
        self.client.force_authenticate(user=self.user)
        data = {'animal_id': self.animal.id}
        self.client.post(self.like_url, data)
        
        # Владелец получает pending мэтчи
        self.client.force_authenticate(user=self.owner)
        pending_url = reverse('pending-matches')
        response = self.client.get(pending_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)