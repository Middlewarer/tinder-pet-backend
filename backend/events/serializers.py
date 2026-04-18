from rest_framework import serializers
from .models import Event, EventParticipant, EventChat, EventMessage
from accounts.serializers import UserSerializer, TagSerializer
from animals.serializers import AnimalSerializer

class EventParticipantSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    animal_detail = AnimalSerializer(source='bring_animal', read_only=True)
    
    class Meta:
        model = EventParticipant
        fields = ['id', 'event', 'user', 'user_detail', 'status', 'bring_animal', 'animal_detail', 'registered_at']
        read_only_fields = ['id', 'registered_at']


class EventSerializer(serializers.ModelSerializer):
    organizer_detail = UserSerializer(source='organizer', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    participants_count = serializers.IntegerField(source='participants.count', read_only=True)
    featured_animals_detail = AnimalSerializer(source='featured_animals', many=True, read_only=True)
    is_participating = serializers.SerializerMethodField()
    participant_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer', 'organizer_detail',
            'start_date', 'end_date', 'location', 'address',
            'cover_image', 'gallery', 'tags', 'tags_detail',
            'max_participants', 'price', 'featured_animals', 'featured_animals_detail',
            'status', 'participants_count', 'is_participating', 'participant_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_is_participating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(user=request.user).exists()
        return False
    
    def get_participant_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.participants.filter(user=request.user).first()
            if participant:
                return participant.status
        return None


class EventChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventChat
        fields = ['id', 'event', 'created_at']


class EventMessageSerializer(serializers.ModelSerializer):
    sender_detail = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = EventMessage
        fields = ['id', 'chat', 'sender', 'sender_detail', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']