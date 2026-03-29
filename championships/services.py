"""
Business logic for championship management.
"""
import math
from itertools import combinations

from .models import Championship, Enrollment, Group, GroupPlayer, GroupStanding
from matches.models import Match


# ──────────────────────────────────────────────
# Group Phase
# ──────────────────────────────────────────────

def generate_groups(championship: Championship, num_groups: int) -> list:
    """
    Distribute enrolled players into groups using snake-draft by ranking.

    Example with 8 players, 2 groups (seed order 1..8):
        Round 1:  1→A, 2→B
        Round 2:  3→B, 4→A   (reversed)
        Round 3:  5→A, 6→B
        ...
    This balances group strength.
    """
    if num_groups < 1:
        raise ValueError('Número de grupos deve ser pelo menos 1.')

    enrollments = (
        Enrollment.objects
        .filter(championship=championship)
        .select_related('player')
        .order_by('seed', '-player__ranking_atual')
    )
    players = [e.player for e in enrollments]

    if len(players) < num_groups:
        raise ValueError(
            f'Apenas {len(players)} inscritos para {num_groups} grupos.'
        )

    # Remove existing groups (cascades to GroupPlayer, GroupStanding, group Matches)
    championship.groups.all().delete()

    group_names = [chr(65 + i) for i in range(num_groups)]
    groups = [
        Group.objects.create(championship=championship, name=n) for n in group_names
    ]

    # Snake draft
    for idx, player in enumerate(players):
        cycle = idx % (num_groups * 2)
        group_idx = cycle if cycle < num_groups else (num_groups * 2 - 1 - cycle)
        GroupPlayer.objects.create(group=groups[group_idx], player=player)
        GroupStanding.objects.create(group=groups[group_idx], player=player)

    return groups


def generate_round_robin(group: Group) -> list:
    """Create all matches for a group (everyone plays everyone once)."""
    Match.objects.filter(group=group).delete()

    player_ids = list(
        group.group_slots.values_list('player_id', flat=True)
    )

    matches = []
    for num, (a_id, b_id) in enumerate(combinations(player_ids, 2), start=1):
        m = Match.objects.create(
            championship=group.championship,
            group=group,
            phase='grupo',
            match_number=num,
            player_a_id=a_id,
            player_b_id=b_id,
        )
        matches.append(m)

    return matches


def calculate_standings(group: Group) -> None:
    """Recalculate all standings for a group from completed matches."""
    standings = {s.player_id: s for s in group.standings.all()}

    for s in standings.values():
        s.wins = s.losses = s.sets_won = s.sets_lost = s.points = 0

    for match in Match.objects.filter(group=group, status='finalizada'):
        if not (match.winner_id and match.player_a_id and match.player_b_id):
            continue

        winner_id = match.winner_id
        loser_id = (
            match.player_b_id if winner_id == match.player_a_id else match.player_a_id
        )

        if winner_id in standings:
            standings[winner_id].wins += 1
            standings[winner_id].points += 3
            standings[winner_id].sets_won += (
                match.score_a if winner_id == match.player_a_id else match.score_b
            )
            standings[winner_id].sets_lost += (
                match.score_b if winner_id == match.player_a_id else match.score_a
            )

        if loser_id in standings:
            standings[loser_id].losses += 1
            standings[loser_id].sets_won += (
                match.score_b if winner_id == match.player_a_id else match.score_a
            )
            standings[loser_id].sets_lost += (
                match.score_a if winner_id == match.player_a_id else match.score_b
            )

    GroupStanding.objects.bulk_update(
        list(standings.values()),
        ['wins', 'losses', 'sets_won', 'sets_lost', 'points'],
    )


def get_group_classified(group: Group, positions: int = 2):
    """Return top N players from a group ordered by standings."""
    standings = group.standings.order_by('-points', '-sets_won', 'sets_lost')
    return [s.player for s in standings[:positions]]


# ──────────────────────────────────────────────
# Elimination Phase
# ──────────────────────────────────────────────

PHASE_ORDER = ['oitavas', 'quartas', 'semi', 'final']
BRACKET_PHASES = {
    2:  ['final'],
    4:  ['semi', 'final'],
    8:  ['quartas', 'semi', 'final'],
    16: ['oitavas', 'quartas', 'semi', 'final'],
}


def generate_elimination_bracket(championship: Championship, players_per_group: int = 2) -> list:
    """
    Build the elimination bracket from group classified players.

    Seeding avoids same-group rematches:
        1st place group A vs 2nd place group B (last group)
        1st place group B vs 2nd place group A (last-1)
        ...
    """
    # Clear existing elimination matches
    Match.objects.filter(championship=championship).exclude(phase='grupo').delete()

    groups = list(championship.groups.all())
    firsts, seconds = [], []

    for g in groups:
        classified = get_group_classified(g, players_per_group)
        if classified:
            firsts.append(classified[0])
        if len(classified) >= 2:
            seconds.append(classified[1])

    # Cross seeding: 1st[i] vs 2nd[n-1-i]
    n = min(len(firsts), len(seconds))
    participants = []
    for i in range(n):
        participants.append(firsts[i])
        participants.append(seconds[n - 1 - i])
    participants += firsts[n:] + seconds[n:]

    total = len(participants)
    if total < 2:
        raise ValueError('São necessários pelo menos 2 classificados.')

    bracket_size = 2 ** math.ceil(math.log2(total))
    phases = BRACKET_PHASES.get(bracket_size, BRACKET_PHASES[16])

    first_round_matches = _create_first_round(championship, participants, bracket_size, phases[0])
    all_matches = list(first_round_matches)

    prev_round = first_round_matches
    for round_idx, phase in enumerate(phases[1:], start=2):
        prev_round, new_matches = _create_next_round(championship, prev_round, phase, round_idx)
        all_matches.extend(new_matches)

    # Auto-advance byes
    for m in first_round_matches:
        if m.status == 'finalizada' and m.winner_id:
            _advance_winner(m)

    return all_matches


def _create_first_round(championship, participants, bracket_size, phase):
    matches = []
    for i in range(0, bracket_size, 2):
        player_a = participants[i] if i < len(participants) else None
        player_b = participants[i + 1] if i + 1 < len(participants) else None

        if player_a and not player_b:
            # Bye: auto-advance
            m = Match.objects.create(
                championship=championship,
                phase=phase,
                round_number=1,
                match_number=i // 2 + 1,
                player_a=player_a,
                winner=player_a,
                status='finalizada',
            )
        elif not player_a and not player_b:
            # Empty slot — both TBD, mark as void bye
            m = Match.objects.create(
                championship=championship,
                phase=phase,
                round_number=1,
                match_number=i // 2 + 1,
                status='finalizada',  # skip in UI
            )
        else:
            m = Match.objects.create(
                championship=championship,
                phase=phase,
                round_number=1,
                match_number=i // 2 + 1,
                player_a=player_a,
                player_b=player_b,
            )
        matches.append(m)
    return matches


def _create_next_round(championship, prev_round, phase, round_idx):
    new_matches = []
    for i in range(0, len(prev_round), 2):
        m = Match.objects.create(
            championship=championship,
            phase=phase,
            round_number=round_idx,
            match_number=i // 2 + 1,
        )
        if i < len(prev_round):
            prev_round[i].next_match = m
            prev_round[i].next_match_slot = 'A'
            prev_round[i].save(update_fields=['next_match', 'next_match_slot'])
        if i + 1 < len(prev_round):
            prev_round[i + 1].next_match = m
            prev_round[i + 1].next_match_slot = 'B'
            prev_round[i + 1].save(update_fields=['next_match', 'next_match_slot'])
        new_matches.append(m)
    return new_matches, new_matches


def _advance_winner(match: Match) -> None:
    if not match.next_match_id or not match.winner_id:
        return
    next_m = match.next_match
    if match.next_match_slot == 'A':
        next_m.player_a = match.winner
    else:
        next_m.player_b = match.winner
    next_m.save(update_fields=['player_a', 'player_b'])


def advance_winner(match: Match) -> None:
    """Public entry point: advance winner and recalculate group standings."""
    _advance_winner(match)
    if match.group_id:
        calculate_standings(match.group)
