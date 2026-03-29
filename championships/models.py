from django.db import models
from players.models import Player


class Championship(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('inscricoes', 'Inscrições Abertas'),
        ('fase_grupos', 'Fase de Grupos'),
        ('eliminatorias', 'Fase Eliminatória'),
        ('finalizado', 'Finalizado'),
    ]

    name = models.CharField('Nome', max_length=200)
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    local = models.CharField('Local', max_length=200)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='rascunho')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Campeonato'
        verbose_name_plural = 'Campeonatos'
        ordering = ['-data_inicio']

    def __str__(self):
        return self.name

    def get_enrolled_players(self):
        return Player.objects.filter(enrollments__championship=self).order_by('-ranking_atual')


class Enrollment(models.Model):
    championship = models.ForeignKey(
        Championship, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Campeonato'
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Jogador'
    )
    seed = models.IntegerField('Seed', default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together = ['championship', 'player']
        ordering = ['seed']

    def __str__(self):
        return f'{self.player} → {self.championship}'


class Group(models.Model):
    championship = models.ForeignKey(
        Championship, on_delete=models.CASCADE, related_name='groups', verbose_name='Campeonato'
    )
    name = models.CharField('Nome', max_length=10)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['name']

    def __str__(self):
        return f'Grupo {self.name} — {self.championship}'

    def get_players(self):
        return Player.objects.filter(group_slots__group=self)


class GroupPlayer(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_slots')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='group_slots')

    class Meta:
        unique_together = ['group', 'player']

    def __str__(self):
        return f'{self.player} — {self.group}'


class GroupStanding(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='standings')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='standings')
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    sets_won = models.IntegerField(default=0)
    sets_lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Classificação do Grupo'
        verbose_name_plural = 'Classificações dos Grupos'
        ordering = ['-points', '-sets_won', 'sets_lost']

    @property
    def sets_balance(self):
        return self.sets_won - self.sets_lost

    def __str__(self):
        return f'{self.player} — {self.group}'
