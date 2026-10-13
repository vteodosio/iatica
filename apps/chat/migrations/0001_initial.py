import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0001_initial'),
        ('groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PerguntaSugerida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=300, verbose_name='Pergunta')),
                ('conceito', models.CharField(blank=True, max_length=120, verbose_name='Conceito demonstrado')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('ativa', models.BooleanField(default=True, verbose_name='Ativa')),
                ('licao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='perguntas_sugeridas', to='content.licao', verbose_name='Lição relacionada')),
            ],
            options={
                'verbose_name': 'Pergunta sugerida',
                'verbose_name_plural': 'Perguntas sugeridas',
                'ordering': ['ordem', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Interacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resposta', models.TextField(verbose_name='Resposta da IA')),
                ('bloqueada', models.BooleanField(default=False, verbose_name='Bloqueada')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interacoes_chat', to=settings.AUTH_USER_MODEL, verbose_name='Aluno')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interacoes_chat', to='groups.grupoestudo', verbose_name='Grupo')),
                ('pergunta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chat.perguntasugerida', verbose_name='Pergunta')),
            ],
            options={
                'verbose_name': 'Interação do chat',
                'verbose_name_plural': 'Interações do chat',
                'ordering': ['criado_em', 'id'],
            },
        ),
    ]
