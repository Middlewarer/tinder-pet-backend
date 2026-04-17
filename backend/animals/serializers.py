from rest_framework import serializers
from .models import Animal, Characteristic

class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['id', 'character']

class AnimalSerializer(serializers.ModelSerializer):
    characteristics = CharacteristicSerializer(many=True, read_only=True, source='characteristic_set')
    
    class Meta:
        model = Animal
        fields = ['id', 'owner', 'name', 'years_of_age', 'description', 'photo', 'characteristics']
        read_only_fields = ['id', 'owner', 'created_at']