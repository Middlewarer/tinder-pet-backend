from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from animals.models import Animal
from interactions.models import Match
from chats.models import Chat, Message

User = get_user_model()

class ChatsAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        
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
            description='Кот'
        )
        
        # Создаем подтвержденный мэтч и чат
        self.match = Match.objects.create(
            user=self.user,
            owner=self.owner,
            animal=self.animal,
            status='matched'
        )
        self.chat = Chat.objects.create(match=self.match)
        
        # Создаем сообщения
        self.message1 = Message.objects.create(
            chat=self.chat,
            sender=self.user,
            text='Привет!'
        )
        self.message2 = Message.objects.create(
            chat=self.chat,
            sender=self.owner,
            text='Здравствуйте!'
        )
    
    def test_get_messages(self):
        """Тест получения сообщений чата"""
        self.client.force_authenticate(user=self.user)
        messages_url = reverse('chat-messages', args=[self.chat.id])
        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_send_message(self):
        """Тест отправки сообщения"""
        self.client.force_authenticate(user=self.user)
        messages_url = reverse('chat-messages', args=[self.chat.id])
        data = {'text': 'Новое сообщение'}
        response = self.client.post(messages_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)
    
    def test_non_participant_cannot_access_chat(self):
        """Тест: неучастник не может получить доступ к чату"""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='other123',
            role='user'
        )
        self.client.force_authenticate(user=other_user)
        messages_url = reverse('chat-messages', args=[self.chat.id])
        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cannot_send_message_to_non_matched_chat(self):
        """Тест: нельзя отправить сообщение в неподтвержденный чат"""
        pending_match = Match.objects.create(
            user=self.user,
            owner=self.owner,
            animal=self.animal,
            status='pending'
        )
        pending_chat = Chat.objects.create(match=pending_match)
        
        self.client.force_authenticate(user=self.user)
        messages_url = reverse('chat-messages', args=[pending_chat.id])
        data = {'text': 'Сообщение'}
        response = self.client.post(messages_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)