from rest_framework import serializers
from .models import User, Preference, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class PreferenceSerializer(serializers.ModelSerializer):
    preferred_tags = TagSerializer(many=True, read_only=True)
    preferred_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='preferred_tags'
    )

    class Meta:
        model = Preference
        fields = ['id', 'user', 'preferred_tags', 'preferred_tag_ids']
        read_only_fields = ['id', 'user']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    preferences = PreferenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'password', 
            'preferences', 'bio', 'avatar', 'phone'  
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Preference.objects.create(user=user)
        return user