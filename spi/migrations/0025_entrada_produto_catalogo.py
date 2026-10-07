from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_catalog_products(apps, schema_editor):
    alias = schema_editor.connection.alias
    Entry = apps.get_model('spi', 'Entrada')
    Product = apps.get_model('spi', 'Produto')
    Control = apps.get_model('spi', 'ControleData')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    products_by_stock = {}
    for entry in Entry.objects.using(alias).select_related('produto').order_by('pk'):
        stock = entry.produto
        if stock.pk not in products_by_stock:
            matches = Product.objects.using(alias).filter(nome=stock.produto)
            if matches.count() > 1:
                matches = matches.filter(descricao=stock.descricao)
            product = matches.first() if matches.count() == 1 else None
            if product is None:
                user_id = entry.usuario_id or User.objects.using(alias).order_by('pk').values_list('pk', flat=True).first()
                if user_id is None:
                    raise RuntimeError('É necessário um usuário para preservar os produtos das entradas antigas.')
                control = Control.objects.using(alias).create(
                    usuario_cadastro_id=user_id, usuario_atualizacao_id=user_id,
                )
                barcode = f'ESTOQUE-{stock.pk}'
                while Product.objects.using(alias).filter(codigo_barras=barcode).exists():
                    barcode += '-LEGADO'
                product = Product.objects.using(alias).create(
                    nome=stock.produto, descricao=stock.descricao,
                    codigo_barras=barcode, responsavel_cadastro_id=user_id,
                    controle_data_id=control.pk,
                )
            products_by_stock[stock.pk] = product.pk
        Entry.objects.using(alias).filter(pk=entry.pk).update(
            produto_catalogo_id=products_by_stock[stock.pk],
        )
    # Resolve verificações adiadas antes das alterações de esquema no PostgreSQL.
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')


class Migration(migrations.Migration):
    dependencies = [
        ('spi', '0024_alter_entrada_ordem_fornecimento_saidaproduto'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='entrada', name='produto_catalogo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='spi.produto', verbose_name='Produto'),
        ),
        migrations.RunPython(copy_catalog_products),
        migrations.RemoveField(model_name='entrada', name='produto'),
        migrations.RenameField(model_name='entrada', old_name='produto_catalogo', new_name='produto'),
        migrations.AlterField(
            model_name='entrada', name='produto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='entradas', to='spi.produto', verbose_name='Produto'),
        ),
    ]
