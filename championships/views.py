from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, View

from .forms import ChampionshipForm, EnrollPlayerForm, GenerateGroupsForm
from .models import Championship, Enrollment, Group, GroupPlayer, GroupStanding
from .services import (
    generate_groups,
    generate_round_robin,
    generate_elimination_bracket,
)
from matches.models import Match
from players.models import Player


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
        from django.db.models import Q
        ctx = super().get_context_data(**kwargs)
        groups = self.object.groups.prefetch_related(
            'standings__player', 'matches__player_a', 'matches__player_b', 'matches__winner'
        ).all()
        ctx['groups'] = groups

        # Anexa played_ids em cada grupo para uso direto no template
        for group in groups:
            finalized = Match.objects.filter(group=group, status='finalizada')
            played_ids = set(
                finalized.values_list('player_a_id', flat=True)
            ) | set(
                finalized.values_list('player_b_id', flat=True)
            )
            played_ids.discard(None)
            group.played_ids = played_ids
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
        bracket = {}
        for match in matches:
            bracket.setdefault(match.get_phase_display(), []).append(match)
        ctx['bracket'] = bracket
        ctx['matches'] = matches

        # Jogadores que já têm partida finalizada nas eliminatórias
        from django.db.models import Q
        elim_finalized = Match.objects.filter(
            championship=self.object,
            status='finalizada',
        ).exclude(phase='grupo')
        elim_played_ids = set(
            elim_finalized.values_list('player_a_id', flat=True)
        ) | set(
            elim_finalized.values_list('player_b_id', flat=True)
        )
        elim_played_ids.discard(None)

        # First-round slots — só jogadores que ainda não jogaram
        first_round_slots = []
        first_round_slots_locked = []
        for match in matches:
            if match.round_number == 1:
                for player, slot_label in [(match.player_a, 'A'), (match.player_b, 'B')]:
                    if not player:
                        continue
                    entry = {
                        'player': player,
                        'match_id': match.pk,
                        'slot': slot_label,
                        'label': f'{player.name} (Partida {match.match_number} — Slot {slot_label})',
                    }
                    if player.pk in elim_played_ids:
                        first_round_slots_locked.append(entry)
                    else:
                        first_round_slots.append(entry)

        ctx['first_round_slots'] = first_round_slots
        ctx['first_round_slots_locked'] = first_round_slots_locked
        return ctx


class SwapBracketPlayersView(View):
    def post(self, request, pk):
        from django.db.models import Q
        championship = get_object_or_404(Championship, pk=pk)
        player1_id = request.POST.get('player1_id')
        player2_id = request.POST.get('player2_id')

        if not player1_id or not player2_id or player1_id == player2_id:
            messages.warning(request, 'Selecione dois jogadores diferentes.')
            return redirect('championships:bracket', pk=pk)

        first_round = (
            Match.objects
            .filter(championship=championship, round_number=1)
            .exclude(phase='grupo')
        )

        match1 = slot1 = match2 = slot2 = None
        for match in first_round:
            if str(match.player_a_id) == player1_id:
                match1, slot1 = match, 'A'
            elif str(match.player_b_id) == player1_id:
                match1, slot1 = match, 'B'
            if str(match.player_a_id) == player2_id:
                match2, slot2 = match, 'A'
            elif str(match.player_b_id) == player2_id:
                match2, slot2 = match, 'B'

        if not match1 or not match2:
            messages.error(request, 'Jogadores não encontrados na primeira rodada.')
            return redirect('championships:bracket', pk=pk)

        # Bloqueia se qualquer um dos dois já tem partida finalizada nas eliminatórias
        p1_id = int(player1_id)
        p2_id = int(player2_id)

        elim_played = Match.objects.filter(
            championship=championship,
            status='finalizada',
        ).exclude(phase='grupo').filter(
            Q(player_a_id__in=[p1_id, p2_id]) | Q(player_b_id__in=[p1_id, p2_id])
        )

        if elim_played.exists():
            names = []
            played_ids = set(
                elim_played.values_list('player_a_id', flat=True)
            ) | set(
                elim_played.values_list('player_b_id', flat=True)
            )
            for pid in [p1_id, p2_id]:
                if pid in played_ids:
                    player = Player.objects.get(pk=pid)
                    names.append(player.name)
            messages.error(
                request,
                f'{" e ".join(names)} já disputou partidas eliminatórias e não pode ser trocado.'
            )
            return redirect('championships:bracket', pk=pk)

        if slot1 == 'A':
            match1.player_a_id = p2_id
        else:
            match1.player_b_id = p2_id

        if slot2 == 'A':
            match2.player_a_id = p1_id
        else:
            match2.player_b_id = p1_id

        match1.save(update_fields=['player_a_id', 'player_b_id'])
        match2.save(update_fields=['player_a_id', 'player_b_id'])

        messages.success(request, 'Posições trocadas na chave.')
        return redirect('championships:bracket', pk=pk)


class MovePlayerGroupView(View):
    def post(self, request, pk):
        from django.db.models import Q
        championship = get_object_or_404(Championship, pk=pk)
        player_id = request.POST.get('player_id')
        source_group_id = request.POST.get('source_group_id')
        target_group_id = request.POST.get('target_group_id')

        if source_group_id == target_group_id:
            messages.warning(request, 'Selecione um grupo diferente.')
            return redirect('championships:groups', pk=pk)

        source_group = get_object_or_404(Group, pk=source_group_id, championship=championship)
        target_group = get_object_or_404(Group, pk=target_group_id, championship=championship)
        player = get_object_or_404(Player, pk=player_id)

        # Bloqueia se o jogador já tem partida finalizada no grupo de origem
        has_played = Match.objects.filter(
            group=source_group,
            status='finalizada',
        ).filter(Q(player_a=player) | Q(player_b=player)).exists()

        if has_played:
            messages.error(
                request,
                f'{player.name} já disputou partidas no Grupo {source_group.name} e não pode ser movido.'
            )
            return redirect('championships:groups', pk=pk)

        if GroupPlayer.objects.filter(group=target_group, player=player).exists():
            messages.error(request, f'{player.name} já está no Grupo {target_group.name}.')
            return redirect('championships:groups', pk=pk)

        GroupPlayer.objects.filter(group=source_group, player=player).update(group=target_group)
        GroupStanding.objects.filter(group=source_group, player=player).update(group=target_group)

        generate_round_robin(source_group)
        generate_round_robin(target_group)

        messages.success(
            request,
            f'{player.name} movido do Grupo {source_group.name} para o Grupo {target_group.name}. Partidas regeneradas.'
        )
        return redirect('championships:groups', pk=pk)
