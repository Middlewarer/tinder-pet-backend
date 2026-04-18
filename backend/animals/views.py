from rest_framework import generics, permissions
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Animal
from interactions.models import Interaction
from accounts.models import Preference
from .serializers import AnimalSerializer


class SwipeAnimalsView(generics.ListAPIView):
    serializer_class = AnimalSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Animal.objects.all()[:50]

        seen_animals = Interactions.objects.filter(user=user).values_list('animal_id', flat=True)

        queryset = Animal.objects.exclude(owner=user).exclude(id__in=seen_animals)

        pref = Preference.objects.filter(user=user).first()
        if pref and pref.preffered_tag:
            queryset = queryset.annotate(
                priority = Case(
                    When(tags__overlap=pref.preffered_tags, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-priority', '-created_at')

        return queryset[:20]




class OwnerAnimalsListView(generics.ListAPIView):
    """Список животных текущего владельца"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем только животных текущего пользователя (если он владелец)
        user = self.request.user
        
        if user.role != 'owner':
            return Animal.objects.none()  # Если не владелец - пустой список
        
        return Animal.objects.filter(owner=user).order_by('-created_at')


class OwnerAnimalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование, удаление животного владельцем"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Только свои животные
        return Animal.objects.filter(owner=self.request.user)
    
    def perform_destroy(self, instance):
        # Дополнительная логика при удалении (опционально)
        print(f"Животное {instance.name} удалено владельцем {self.request.user.username}")
        instance.delete()
