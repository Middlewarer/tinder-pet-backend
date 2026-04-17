from rest_framework import serializers
from .models import Interaction, Match
from animals.serializers import AnimalSerializer
from accounts.serializers import UserSerializer

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ['id', 'user', 'animal', 'type', 'created_at']
        read_only_fields = ['id', 'created_at']

class MatchSerializer(serializers.ModelSerializer):
    animal_detail = AnimalSerializer(source='animal', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    owner_detail = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'user', 'owner', 'animal', 'animal_detail', 'user_detail', 'owner_detail', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']