from django.db import models
from django.conf import settings

class Animal(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animals')
    name = models.CharField(max_length=100)
    years_of_age = models.IntegerField(default=1)
    description = models.TextField()
    photo = models.ImageField(upload_to='pets/pet_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Characteristic(models.Model):
    DEFAULT_CHOICES = (
        ('calm', 'спокойный'),
        ('active', 'активный'),
        ('kid_friendly', 'для детей'),
        ('guide', 'поводырь')
    )

    pet = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='characteristics')
    character = models.CharField(max_length=20, choices=DEFAULT_CHOICES, default='calm')