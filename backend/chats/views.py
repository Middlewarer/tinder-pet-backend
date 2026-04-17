from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Chat, Message
from .serializers import MessageSerializer

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        # Проверка: участник ли чата
        if self.request.user not in [chat.match.user, chat.match.owner]:
            raise PermissionDenied("Not a participant")
        
        return Message.objects.filter(chat=chat).order_by('created_at')
    
    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        if self.request.user not in [chat.match.user, chat.match.owner]:
            raise PermissionDenied("Not a participant")
        
        # Проверка: матч должен быть confirmed
        if chat.match.status != 'matched':
            raise PermissionDenied("Match not confirmed yet")
        
        serializer.save(chat=chat, sender=self.request.user)