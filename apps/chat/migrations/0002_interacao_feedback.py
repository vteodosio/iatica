from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interacao',
            name='feedback',
            field=models.CharField(blank=True, choices=[('ajudou', 'Ajudou'), ('errou', 'Acho que a IA errou')], max_length=10, verbose_name='Avaliação do aluno'),
        ),
    ]
