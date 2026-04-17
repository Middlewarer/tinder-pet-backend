from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Interaction, Match
from animals.models import Animal
from chats.models import Chat

class LikeView(views.APIView):
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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