from django.contrib import admin

# Register your models here.

#chats
from .models import *

admin.site.register(Message)

admin.site.register(Chat)