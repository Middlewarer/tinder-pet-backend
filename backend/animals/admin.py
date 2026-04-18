from django.contrib import admin

# Register your models here.
#animals
from .models import *

admin.site.register(Animal)

admin.site.register(Characteristic)