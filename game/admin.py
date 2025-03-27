from django.contrib import admin

from .models import GameSession, GameSessionStats

# Register your models here.

admin.site.register(GameSession)
admin.site.register(GameSessionStats)
