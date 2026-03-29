from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'categoria', 'ranking_atual', 'created_at']
    list_filter = ['categoria']
    search_fields = ['name']
    ordering = ['-ranking_atual']
