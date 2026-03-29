from django.db import models

CATEGORY_CHOICES = [
    ('iniciante', 'Iniciante'),
    ('intermediario', 'Intermediário'),
    ('avancado', 'Avançado'),
]


class Player(models.Model):
    name = models.CharField('Nome', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Jogador'
        verbose_name_plural = 'Jogadores'
        ordering = ['name']

    def __str__(self):
        return self.name


class PlayerCategoryRanking(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='category_rankings', verbose_name='Jogador'
    )
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES)
    pontos = models.IntegerField('Pontos', default=1000)

    class Meta:
        verbose_name = 'Ranking por Categoria'
        verbose_name_plural = 'Rankings por Categoria'
        unique_together = [('player', 'categoria')]
        ordering = ['-pontos']

    def __str__(self):
        return f'{self.player.name} — {self.get_categoria_display()}: {self.pontos} pts'
