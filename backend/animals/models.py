from django.db import models

class Animal(models.Model):
    owner = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    years_of_age = models.IntegerField(default=1)
    description = models.TextField()
    photo = models.ImageField(upload_to='pets/pet_images/')
    
class Characteristic(models.Model):
    DEFAULT_CHOICES = (
        ('calm', 'спокойный'),
        ('active', 'активный'),
        ('kid_friendly', 'для детей'),
        ('guide', 'поводырь')
    )

    pet = models.ForeignKey(Animal, on_delete=models.CASCADE)
    character = models.CharField(max_length=20, choices=DEFAULT_CHOICES, default='calm')

