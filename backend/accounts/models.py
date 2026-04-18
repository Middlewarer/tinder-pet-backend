from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User ( ищет животное )'),
        ('owner', 'Owner (владелец животного )'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    bio = models.TextField(max_length=500, blank=True, null=True) 
    avatar = models.URLField(blank=True, null=True)  
    phone = models.CharField(max_length=20, blank=True, null=True)  

    groups = models.ManyToManyField('auth.Group', related_name='tinder_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='tinder_user_permissions', blank=True)

class Tag(models.Model):
    DEFAULT_CHOICES = (
        ('calm', 'спокойный'),
        ('active', 'активный'),
        ('kid_friendly', 'для детей'),
        ('guide', 'поводырь')
    )
    
    name = models.CharField(max_length=50, unique=True, choices=DEFAULT_CHOICES)

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_tags = models.ManyToManyField(Tag, blank=True)