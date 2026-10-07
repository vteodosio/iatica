from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='apelido',
            field=models.CharField(blank=True, help_text='Nome ou apelido exibido para os alunos (não precisa ser o nome real).', max_length=120, verbose_name='Apelido / Nome de exibição'),
        ),
        migrations.AddField(
            model_name='user',
            name='consentiu_em',
            field=models.DateTimeField(blank=True, help_text='Data/hora em que o aluno (ou responsável) aceitou o aviso de privacidade.', null=True, verbose_name='Consentimento registrado em'),
        ),
    ]
