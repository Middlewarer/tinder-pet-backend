from rest_framework import generics, permissions
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Animal
from interactions.models import Interaction
from accounts.models import Preference
from .serializers import AnimalSerializer


class SwipeAnimalsView(generics.ListAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

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
