from django.contrib import admin
from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'championship', 'phase', 'status', 'score_a', 'score_b', 'winner']
    list_filter = ['championship', 'phase', 'status']
    search_fields = ['player_a__name', 'player_b__name']
    readonly_fields = ['winner']
