from django.db import models
from accounts.models import User
from animals.models import Animal

class Interaction(models.Model):
    TYPE_CHOICES = (('like', 'like'), ('dislike', 'dislike'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'animal')

class Match(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('matched', 'Принят'),
        ('rejected', 'Отклонен')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user')
    owner = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='matches_as_owner')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    