from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Chat, Message
from .serializers import MessageSerializer, ChatSerializer
# from .serializers import ChatSerializer, MessageSerializer

from django.db import models

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        return Message.objects.filter(chat=chat).order_by('created_at')
    
    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        
        serializer.save(chat=chat, sender=self.request.user)



class ChatListView(generics.ListAPIView):
    """Список чатов пользователя"""
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            models.Q(match__user=user) | models.Q(match__owner=user)
        ).order_by('-created_at')


class ChatDetailView(generics.RetrieveAPIView):
    """Детали чата"""
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            models.Q(match__user=user) | models.Q(match__owner=user)
        )


class ChatDeleteView(generics.DestroyAPIView):
    """Удалить чат"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            models.Q(match__user=user) | models.Q(match__owner=user)
        )