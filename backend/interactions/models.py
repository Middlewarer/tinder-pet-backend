from django.db import models
from accounts.models import User
from animals.models import Animal

class Interaction(models.Model):
    TYPE_CHOICES = (('like', 'like'), ('dislike', 'dislike'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'animal')

    def __str__(self):
        return f'{self.user.username} with animal {self.animal.name}'

class Match(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('matched', 'Принят'),
        ('rejected', 'Отклонен')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_owner')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='matches')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'user: {self.user.username} owner: {self.owner.username}'