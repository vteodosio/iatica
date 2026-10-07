import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pergunta',
            name='explicacao',
            field=models.TextField(blank=True, help_text='Por que a resposta correta está certa. Exibida ao aluno no resultado.', verbose_name='Explicação'),
        ),
        migrations.AddField(
            model_name='pergunta',
            name='licao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='perguntas', to='content.licao', verbose_name='Lição relacionada'),
        ),
    ]
