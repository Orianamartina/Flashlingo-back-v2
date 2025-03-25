from django.contrib import admin

from .models import GameSession, GameSessionStats, GermanWord

# Register your models here.

admin.site.register(GermanWord)
admin.site.register(GameSession)
admin.site.register(GameSessionStats)
