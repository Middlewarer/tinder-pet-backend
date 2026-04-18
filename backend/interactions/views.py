from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework import permissions
from .models import Interaction, Match
from animals.models import Animal
from chats.models import Chat

from .serializers import MatchSerializer



class LikeView(views.APIView):
    
    def post(self, request):
        user = request.user
        animal_id = request.data.get('animal_id')
        
        # Проверка: существует ли животное
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return Response({'error': 'Animal not found'}, status=404)
        
        # Нельзя лайкнуть своё
        if animal.owner == user:
            return Response({'error': 'Cannot like own animal'}, status=400)
        
        # Нельзя повторно лайкнуть
        if Interaction.objects.filter(user=user, animal=animal).exists():
            return Response({'error': 'Already interacted'}, status=400)
        
        # Создаём лайк
        Interaction.objects.create(user=user, animal=animal, type='like')
        
        # Создаём мэтч со статусом pending
        match = Match.objects.create(
            user=user,
            owner=animal.owner,
            animal=animal,
            status='pending'
        )
        
        return Response({'match_id': match.id, 'status': 'pending'})

class AcceptMatchView(views.APIView):

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, owner=request.user, status='pending')
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=404)
        
        match.status = 'matched'
        match.save()
        
        # Создаём чат
        chat = Chat.objects.create(match=match)
        
        return Response({'match_id': match.id, 'chat_id': chat.id})


class PendingMatchesView(generics.ListAPIView):
    """Список ожидающих мэтчей для владельца"""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'owner':
            return Match.objects.none()
        return Match.objects.filter(owner=self.request.user, status='pending')


class AcceptedMatchesView(generics.ListAPIView):
    """Список принятых мэтчей"""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'owner':
            return Match.objects.filter(owner=user, status='matched')
        return Match.objects.filter(user=user, status='matched')


class RejectMatchView(generics.UpdateAPIView):
    """Отклонить мэтч"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, owner=request.user, status='pending')
            match.status = 'rejected'
            match.save()
            return Response({'status': 'rejected'})
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)


class SentLikesView(generics.ListAPIView):
    """Каких животных лайкнул пользователь"""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Match.objects.filter(user=self.request.user)


class ReceivedLikesView(generics.ListAPIView):
    """Кто лайкнул животных владельца"""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'owner':
            return Match.objects.none()
        return Match.objects.filter(owner=self.request.user, status='pending')

