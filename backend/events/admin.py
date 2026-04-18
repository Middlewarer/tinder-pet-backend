from django.contrib import admin

from . models import *

admin.site.register(Event)
admin.site.register(EventChat)
admin.site.register(EventMessage)
admin.site.register(EventParticipant)
