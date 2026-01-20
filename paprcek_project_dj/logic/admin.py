from django.contrib import admin
from .models import LogicScore

@admin.register(LogicScore)
class LogicScoreAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'time', 'created_at')
    ordering = ('time',)