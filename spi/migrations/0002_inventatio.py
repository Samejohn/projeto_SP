import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spi', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_patrimonio', models.CharField(max_length=30, unique=True, verbose_name='Nº Patrimônio')),
                ('id_ativo', models.CharField(max_length=30, unique=True, verbose_name='ID do Inventario')),
                ('categoria', models.CharField(choices=[('NOTE', 'Notebook'), ('DESK', 'Desktop'), ('MONI', 'Monitor'), ('IMP', 'Impressora'), ('NOBR', 'Nobreak'), ('SERV', 'Servidor'), ('OUTR', 'Outros')], max_length=20, verbose_name='Categoria')),
                ('item_modelo', models.CharField(max_length=150, verbose_name='Item / Modelo')),
                ('serie_licenca', models.CharField(blank=True, max_length=150, null=True, verbose_name='S/N (Série) / Licença')),
                ('data_aquisicao', models.DateField(verbose_name='Data Aquisição')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor (R$)')),
                ('validade_garantia', models.DateField(blank=True, null=True, verbose_name='Validade / Garantia')),
                ('status', models.CharField(choices=[('ATIVO', 'Ativo'), ('MANUT', 'Em Manutenção'), ('DESC', 'Descartado')], default='ATIVO', max_length=15, verbose_name='Status')),
                ('setor', models.CharField(max_length=100, verbose_name='Setor')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Inventario',
                'verbose_name_plural': 'inventarios',
                'ordering': ['numero_patrimonio'],
            },
        ),
    ]
