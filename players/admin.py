from django.contrib import admin
from .models import Player, PlayerCategoryRanking


class PlayerCategoryRankingInline(admin.TabularInline):
    model = PlayerCategoryRanking
    extra = 0


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    inlines = [PlayerCategoryRankingInline]


@admin.register(PlayerCategoryRanking)
class PlayerCategoryRankingAdmin(admin.ModelAdmin):
    list_display = ['player', 'categoria', 'pontos']
    list_filter = ['categoria']
    ordering = ['categoria', '-pontos']
