from django.db import models
from interactions.models import Match
from accounts.models import User

class Chat(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)