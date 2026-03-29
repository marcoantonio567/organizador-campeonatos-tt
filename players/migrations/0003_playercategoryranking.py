from django.db import migrations, models
import django.db.models.deletion


def migrate_rankings(apps, schema_editor):
    """Cria um PlayerCategoryRanking para cada jogador usando sua categoria e ranking_atual existentes."""
    Player = apps.get_model('players', 'Player')
    PlayerCategoryRanking = apps.get_model('players', 'PlayerCategoryRanking')
    for player in Player.objects.all():
        PlayerCategoryRanking.objects.create(
            player=player,
            categoria=player.categoria,
            pontos=player.ranking_atual,
        )


def reverse_migrate(apps, schema_editor):
    PlayerCategoryRanking = apps.get_model('players', 'PlayerCategoryRanking')
    PlayerCategoryRanking.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_alter_player_categoria'),
    ]

    operations = [
        # 1. Cria o novo modelo
        migrations.CreateModel(
            name='PlayerCategoryRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(
                    choices=[
                        ('iniciante', 'Iniciante'),
                        ('intermediario', 'Intermediário'),
                        ('avancado', 'Avançado'),
                    ],
                    max_length=20,
                    verbose_name='Categoria',
                )),
                ('pontos', models.IntegerField(default=1000, verbose_name='Pontos')),
                ('player', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='category_rankings',
                    to='players.player',
                    verbose_name='Jogador',
                )),
            ],
            options={
                'verbose_name': 'Ranking por Categoria',
                'verbose_name_plural': 'Rankings por Categoria',
                'ordering': ['-pontos'],
                'unique_together': {('player', 'categoria')},
            },
        ),
        # 2. Migra os dados existentes
        migrations.RunPython(migrate_rankings, reverse_migrate),
        # 3. Remove os campos antigos do Player
        migrations.RemoveField(
            model_name='player',
            name='categoria',
        ),
        migrations.RemoveField(
            model_name='player',
            name='ranking_atual',
        ),
        # 4. Atualiza o ordering do Player
        migrations.AlterModelOptions(
            name='player',
            options={
                'ordering': ['name'],
                'verbose_name': 'Jogador',
                'verbose_name_plural': 'Jogadores',
            },
        ),
    ]
