from django.db import models
from django.conf import settings
from accounts.models import User, Tag

class Event(models.Model):
    """Мероприятие (выставка, встреча, мастер-класс и т.д.)"""
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )
    
    # Основная информация
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    organizer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='organized_events',
        verbose_name='Организатор'
    )
    
    # Время и место
    start_date = models.DateTimeField(verbose_name='Дата и время начала')
    end_date = models.DateTimeField(verbose_name='Дата и время окончания')
    location = models.CharField(max_length=300, verbose_name='Место проведения')
    address = models.CharField(max_length=500, blank=True, null=True, verbose_name='Адрес')
    
    # Медиа
    cover_image = models.URLField(blank=True, null=True, verbose_name='Обложка')
    gallery = models.JSONField(default=list, blank=True, verbose_name='Галерея фото')
    
    # Дополнительно
    tags = models.ManyToManyField(Tag, blank=True, related_name='events', verbose_name='Теги')
    max_participants = models.IntegerField(default=0, verbose_name='Максимум участников (0 - безлимит)')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость')
    
    # Связь с животными (опционально)
    featured_animals = models.ManyToManyField(
        'animals.Animal', 
        blank=True, 
        related_name='featured_events',
        verbose_name='Представленные животные'
    )
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d.%m.%Y')}"


class EventParticipant(models.Model):
    """Участник мероприятия"""
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('approved', 'Подтверждён'),
        ('rejected', 'Отклонён'),
        ('cancelled', 'Отменён'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_participating')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Для владельцев животных - возможность привести питомца
    bring_animal = models.ForeignKey(
        'animals.Animal', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='events_to_attend',
        verbose_name='Приведу животное'
    )
    
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.status})"


class EventChat(models.Model):
    """Чат мероприятия"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat for {self.event.title}"


class EventMessage(models.Model):
    """Сообщение в чате мероприятия"""
    chat = models.ForeignKey(EventChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_messages')
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"