from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Player, PlayerCategoryRanking, CATEGORY_CHOICES
from .forms import PlayerForm, PlayerCategoryRankingForm

_CATEGORY_FIELD_MAP = [
    ('iniciante',     'pontos_iniciante'),
    ('intermediario', 'pontos_intermediario'),
    ('avancado',      'pontos_avancado'),
]


class PlayerListView(ListView):
    model = Player
    template_name = 'players/list.html'
    context_object_name = 'players'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = [
            (
                key,
                label,
                PlayerCategoryRanking.objects
                    .filter(categoria=key)
                    .select_related('player')
                    .order_by('-pontos'),
            )
            for key, label in CATEGORY_CHOICES
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
        ctx['category_rankings'] = player.category_rankings.order_by('categoria')
        return ctx


class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Novo Jogador'
        ctx['ranking_form'] = PlayerCategoryRankingForm(self.request.POST or None)
        return ctx

    def form_valid(self, form):
        player = form.save()
        ranking_form = PlayerCategoryRankingForm(self.request.POST)
        if ranking_form.is_valid():
            for cat_key, field_name in _CATEGORY_FIELD_MAP:
                pontos = ranking_form.cleaned_data.get(field_name)
                if pontos is not None:
                    PlayerCategoryRanking.objects.create(
                        player=player, categoria=cat_key, pontos=pontos
                    )
        return redirect(self.success_url)


class PlayerUpdateView(UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def _initial_ranking_data(self):
        return {
            f'pontos_{r.categoria}': r.pontos
            for r in self.object.category_rankings.all()
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Editar — {self.object.name}'
        if self.request.POST:
            ctx['ranking_form'] = PlayerCategoryRankingForm(self.request.POST)
        else:
            ctx['ranking_form'] = PlayerCategoryRankingForm(
                initial=self._initial_ranking_data()
            )
        return ctx

    def form_valid(self, form):
        player = form.save()
        ranking_form = PlayerCategoryRankingForm(self.request.POST)
        if ranking_form.is_valid():
            for cat_key, field_name in _CATEGORY_FIELD_MAP:
                pontos = ranking_form.cleaned_data.get(field_name)
                if pontos is not None:
                    PlayerCategoryRanking.objects.update_or_create(
                        player=player, categoria=cat_key,
                        defaults={'pontos': pontos},
                    )
                else:
                    PlayerCategoryRanking.objects.filter(
                        player=player, categoria=cat_key
                    ).delete()
        return redirect(self.success_url)


class PlayerDeleteView(DeleteView):
    model = Player
    template_name = 'players/confirm_delete.html'
    success_url = reverse_lazy('players:list')
    context_object_name = 'player'
