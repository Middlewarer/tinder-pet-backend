from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Preference, Tag
from .serializers import UserSerializer, TagSerializer, PreferenceSerializer

# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class TagListView(generics.ListAPIView):
    """Список всех тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class PreferenceView(generics.RetrieveUpdateAPIView):
    """Получение и обновление предпочтений пользователя"""
    serializer_class = PreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = Preference.objects.get_or_create(user=self.request.user)
        return preference




