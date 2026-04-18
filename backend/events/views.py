from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Event, EventParticipant, EventChat, EventMessage
from .serializers import (
    EventSerializer, EventParticipantSerializer, 
    EventChatSerializer, EventMessageSerializer
)


class EventListView(generics.ListCreateAPIView):
    """Список мероприятий и создание нового"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.filter(status='active')
        
        # Фильтрация по параметрам
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Поиск по названию
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # Фильтр по дате
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            from django.utils import timezone
            queryset = queryset.filter(start_date__gte=timezone.now())
        
        # Мои мероприятия (как организатор)
        my_events = self.request.query_params.get('my_events')
        if my_events == 'true':
            queryset = queryset.filter(organizer=user)
        
        # Мероприятия, где я участник
        my_participation = self.request.query_params.get('my_participation')
        if my_participation == 'true':
            queryset = queryset.filter(participants__user=user)
        
        return queryset.order_by('start_date')
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали мероприятия, обновление, удаление"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Организатор может видеть всё, остальные - только активные
        if user.role == 'owner' or user.is_superuser:
            return Event.objects.all()
        return Event.objects.filter(Q(status='active') | Q(organizer=user))
    
    def perform_update(self, serializer):
        event = self.get_object()
        if event.organizer != self.request.user and not self.request.user.is_superuser:
            return Response(
                {"detail": "Только организатор может редактировать мероприятие"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.organizer != self.request.user and not self.request.user.is_superuser:
            return Response(
                {"detail": "Только организатор может удалить мероприятие"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


class EventParticipantView(generics.GenericAPIView):
    """Управление участниками мероприятия"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, event_id):
        """Записаться на мероприятие"""
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Мероприятие не найдено"}, status=404)
        
        # Проверка лимита участников
        if event.max_participants > 0 and event.participants.count() >= event.max_participants:
            return Response({"error": "Лимит участников превышен"}, status=400)
        
        participant, created = EventParticipant.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'status': 'approved' if event.organizer == request.user else 'pending'}
        )
        
        if not created:
            return Response({"error": "Вы уже записаны"}, status=400)
        
        # Создаём чат для мероприятия, если его нет
        EventChat.objects.get_or_create(event=event)
        
        return Response(EventParticipantSerializer(participant).data, status=201)
    
    def delete(self, request, event_id):
        """Отменить запись на мероприятие"""
        try:
            participant = EventParticipant.objects.get(event_id=event_id, user=request.user)
            participant.delete()
            return Response({"detail": "Участие отменено"})
        except EventParticipant.DoesNotExist:
            return Response({"error": "Вы не записаны"}, status=404)


class EventParticipantsListView(generics.ListAPIView):
    """Список участников мероприятия (для организатора)"""
    serializer_class = EventParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        event_id = self.kwargs['event_id']
        try:
            event = Event.objects.get(id=event_id)
            if event.organizer != self.request.user and not self.request.user.is_superuser:
                return EventParticipant.objects.none()
            return EventParticipant.objects.filter(event_id=event_id)
        except Event.DoesNotExist:
            return EventParticipant.objects.none()


class EventParticipantStatusView(generics.UpdateAPIView):
    """Подтверждение/отклонение участника (для организатора)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, event_id, participant_id):
        try:
            event = Event.objects.get(id=event_id)
            if event.organizer != request.user and not request.user.is_superuser:
                return Response({"error": "Нет прав"}, status=403)
            
            participant = EventParticipant.objects.get(id=participant_id, event_id=event_id)
            new_status = request.data.get('status')
            
            if new_status not in ['approved', 'rejected']:
                return Response({"error": "Неверный статус"}, status=400)
            
            participant.status = new_status
            participant.save()
            return Response(EventParticipantSerializer(participant).data)
        except Event.DoesNotExist:
            return Response({"error": "Мероприятие не найдено"}, status=404)
        except EventParticipant.DoesNotExist:
            return Response({"error": "Участник не найден"}, status=404)


class EventChatMessagesView(generics.ListCreateAPIView):
    """Чат мероприятия - получение и отправка сообщений"""
    serializer_class = EventMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        event_id = self.kwargs['event_id']
        try:
            # Проверяем, что пользователь - участник или организатор
            event = Event.objects.get(id=event_id)
            is_participant = event.participants.filter(user=self.request.user).exists()
            
            if not is_participant and event.organizer != self.request.user:
                return EventMessage.objects.none()
            
            chat, _ = EventChat.objects.get_or_create(event=event)
            return EventMessage.objects.filter(chat=chat)
        except Event.DoesNotExist:
            return EventMessage.objects.none()
    
    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(id=event_id)
        chat, _ = EventChat.objects.get_or_create(event=event)
        serializer.save(chat=chat, sender=self.request.user)