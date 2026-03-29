from django.contrib import admin
from .models import Championship, Enrollment, Group, GroupPlayer, GroupStanding


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['player', 'seed']


class GroupPlayerInline(admin.TabularInline):
    model = GroupPlayer
    extra = 0


class GroupStandingInline(admin.TabularInline):
    model = GroupStanding
    extra = 0
    readonly_fields = ['wins', 'losses', 'sets_won', 'sets_lost', 'points']


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_inicio', 'local', 'finalizado']
    list_filter = ['finalizado']
    search_fields = ['name']
    inlines = [EnrollmentInline]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'championship']
    list_filter = ['championship']
    inlines = [GroupPlayerInline, GroupStandingInline]


@admin.register(GroupStanding)
class GroupStandingAdmin(admin.ModelAdmin):
    list_display = ['player', 'group', 'points', 'wins', 'losses', 'sets_won', 'sets_lost']
    list_filter = ['group__championship']
