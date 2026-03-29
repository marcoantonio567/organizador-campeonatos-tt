from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Player
from .forms import PlayerForm


class PlayerListView(ListView):
    model = Player
    template_name = 'players/list.html'
    context_object_name = 'players'
    ordering = ['-ranking_atual']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['categories'] = [
            ('avancado',      'Avançado',      qs.filter(categoria='avancado')),
            ('intermediario', 'Intermediário', qs.filter(categoria='intermediario')),
            ('iniciante',     'Iniciante',     qs.filter(categoria='iniciante')),
        ]
        return ctx


class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/detail.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = self.object

        from matches.models import Match
        finished = Match.objects.filter(
            Q(player_a=player) | Q(player_b=player),
            status='finalizada'
        )

        total = finished.count()
        wins  = finished.filter(winner=player).count()

        # Sets vencidos = soma dos sets do lado do jogador em cada partida
        sets_as_a = finished.filter(player_a=player).aggregate(s=Sum('score_a'))['s'] or 0
        sets_as_b = finished.filter(player_b=player).aggregate(s=Sum('score_b'))['s'] or 0
        total_sets_won = sets_as_a + sets_as_b

        ctx['stats'] = {
            'total_matches': total,
            'wins':          wins,
            'losses':        total - wins,
            'win_pct':       round(wins / total * 100) if total else 0,
            'total_sets_won': total_sets_won,
        }
        return ctx


class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Novo Jogador'
        return ctx


class PlayerUpdateView(UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Editar — {self.object.name}'
        return ctx


class PlayerDeleteView(DeleteView):
    model = Player
    template_name = 'players/confirm_delete.html'
    success_url = reverse_lazy('players:list')
    context_object_name = 'player'
