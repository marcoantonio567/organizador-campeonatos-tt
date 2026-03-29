from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, View

from .forms import ChampionshipForm, EnrollPlayerForm, GenerateGroupsForm
from .models import Championship, Enrollment, Group
from .services import (
    generate_groups,
    generate_round_robin,
    generate_elimination_bracket,
)
from matches.models import Match


class ChampionshipListView(ListView):
    model = Championship
    template_name = 'championships/list.html'
    context_object_name = 'championships'

    def get_context_data(self, **kwargs):
        from datetime import date
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        ctx['ativos']    = Championship.objects.filter(data_inicio__gte=today).order_by('-data_inicio')
        ctx['historico'] = Championship.objects.filter(data_inicio__lt=today).order_by('-data_inicio')
        ctx['today'] = today
        return ctx


class ChampionshipCreateView(CreateView):
    model = Championship
    form_class = ChampionshipForm
    template_name = 'championships/form.html'
    success_url = reverse_lazy('championships:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Novo Campeonato'
        return ctx


class ChampionshipUpdateView(UpdateView):
    model = Championship
    form_class = ChampionshipForm
    template_name = 'championships/form.html'

    def get_success_url(self):
        return reverse('championships:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Editar — {self.object.name}'
        return ctx


class ChampionshipDetailView(DetailView):
    model = Championship
    template_name = 'championships/detail.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        championship = self.object
        ctx['enrollments'] = championship.enrollments.select_related('player').order_by('seed')
        ctx['enroll_form'] = EnrollPlayerForm(championship)
        ctx['generate_groups_form'] = GenerateGroupsForm()
        ctx['has_bracket'] = championship.matches.exclude(phase='grupo').exists()
        return ctx


class ChampionshipDeleteView(DeleteView):
    model = Championship
    template_name = 'championships/confirm_delete.html'
    success_url = reverse_lazy('championships:list')
    context_object_name = 'championship'


class EnrollPlayerView(View):
    def post(self, request, pk):
        championship = get_object_or_404(Championship, pk=pk)
        form = EnrollPlayerForm(championship, request.POST)
        if form.is_valid():
            player = form.cleaned_data['player']
            seed = championship.enrollments.count() + 1
            Enrollment.objects.create(championship=championship, player=player, seed=seed)
            messages.success(request, f'{player.name} inscrito com sucesso.')
        else:
            messages.error(request, 'Erro ao inscrever jogador.')
        return redirect('championships:detail', pk=pk)


class RemoveEnrollmentView(View):
    def post(self, request, pk, enrollment_pk):
        enrollment = get_object_or_404(Enrollment, pk=enrollment_pk, championship_id=pk)
        enrollment.delete()
        messages.success(request, 'Inscrição removida.')
        return redirect('championships:detail', pk=pk)


class GenerateGroupsView(View):
    def post(self, request, pk):
        championship = get_object_or_404(Championship, pk=pk)
        form = GenerateGroupsForm(request.POST)
        if form.is_valid():
            try:
                num_groups = form.cleaned_data['num_groups']
                groups = generate_groups(championship, num_groups)
                for group in groups:
                    generate_round_robin(group)
                messages.success(request, f'{len(groups)} grupos gerados com sucesso.')
            except ValueError as e:
                messages.error(request, str(e))
        return redirect('championships:groups', pk=pk)


class GroupsView(DetailView):
    model = Championship
    template_name = 'championships/groups.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        groups = self.object.groups.prefetch_related(
            'standings__player', 'matches__player_a', 'matches__player_b', 'matches__winner'
        ).all()
        ctx['groups'] = groups
        return ctx


class GenerateEliminationView(View):
    def post(self, request, pk):
        championship = get_object_or_404(Championship, pk=pk)
        try:
            generate_elimination_bracket(championship)
            messages.success(request, 'Chave eliminatória gerada com sucesso.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('championships:bracket', pk=pk)


class BracketView(DetailView):
    model = Championship
    template_name = 'championships/bracket.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        matches = (
            Match.objects
            .filter(championship=self.object)
            .exclude(phase='grupo')
            .select_related('player_a', 'player_b', 'winner')
            .order_by('round_number', 'match_number')
        )
        # Group by phase
        from itertools import groupby
        bracket = {}
        for match in matches:
            bracket.setdefault(match.get_phase_display(), []).append(match)
        ctx['bracket'] = bracket
        ctx['matches'] = matches
        return ctx
