from django.db import models


class Player(models.Model):
    CATEGORY_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    name = models.CharField('Nome', max_length=100)
    ranking_atual = models.IntegerField('Ranking (pontos)', default=1000)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES, default='iniciante')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Jogador'
        verbose_name_plural = 'Jogadores'
        ordering = ['-ranking_atual']

    def __str__(self):
        return self.name
