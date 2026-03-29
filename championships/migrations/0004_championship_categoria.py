from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championships', '0003_remove_championship_status_championship_finalizado'),
    ]

    operations = [
        migrations.AddField(
            model_name='championship',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('iniciante', 'Iniciante'),
                    ('intermediario', 'Intermediário'),
                    ('avancado', 'Avançado'),
                ],
                default='iniciante',
                max_length=20,
                verbose_name='Categoria',
            ),
        ),
    ]
