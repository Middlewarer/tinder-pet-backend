from rest_framework import serializers
from .models import Chat, Message
from accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_detail = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'sender_detail', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = ['id', 'match', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at']