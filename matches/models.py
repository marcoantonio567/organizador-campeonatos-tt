from django.db import models
from players.models import Player
from championships.models import Championship, Group


class Match(models.Model):
    PHASE_CHOICES = [
        ('grupo', 'Fase de Grupos'),
        ('oitavas', 'Oitavas de Final'),
        ('quartas', 'Quartas de Final'),
        ('semi', 'Semifinal'),
        ('terceiro', 'Disputa de 3º Lugar'),
        ('final', 'Final'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('finalizada', 'Finalizada'),
    ]

    championship = models.ForeignKey(
        Championship, on_delete=models.CASCADE, related_name='matches', verbose_name='Campeonato'
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches', verbose_name='Grupo'
    )
    phase = models.CharField('Fase', max_length=20, choices=PHASE_CHOICES, default='grupo')
    round_number = models.IntegerField('Rodada', default=1)
    match_number = models.IntegerField('Número da Partida', default=1)

    player_a = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='matches_as_a', verbose_name='Jogador A'
    )
    player_b = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='matches_as_b', verbose_name='Jogador B'
    )
    score_a = models.IntegerField('Sets Jogador A', default=0)
    score_b = models.IntegerField('Sets Jogador B', default=0)
    winner = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='match_wins', verbose_name='Vencedor'
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')

    # Bracket linking
    next_match = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='previous_matches', verbose_name='Próxima Partida'
    )
    next_match_slot = models.CharField(
        max_length=1, choices=[('A', 'Slot A'), ('B', 'Slot B')], null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
        ordering = ['round_number', 'match_number']

    def __str__(self):
        a = self.player_a or 'A definir'
        b = self.player_b or 'A definir'
        return f'{self.get_phase_display()}: {a} vs {b}'

    def save(self, *args, **kwargs):
        if self.status == 'finalizada' and self.player_a and self.player_b:
            if self.score_a > self.score_b:
                self.winner = self.player_a
            elif self.score_b > self.score_a:
                self.winner = self.player_b
        super().save(*args, **kwargs)
