"""Integra as entradas e saídas ao saldo, dentro da mesma transação."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F


def find_or_create_product_stock(product, unit_price):
    from spi.models import Estoque, Produto

    # O vínculo pelo ID continua correto mesmo quando o nome do produto muda.
    product_stock = Estoque.objects.select_for_update().filter(produto_catalogo=product).first()
    if product_stock is None:
        legacy_stocks = list(Estoque.objects.select_for_update().filter(
            produto=product.nome, produto_catalogo__isnull=True,
        ))
        if len(legacy_stocks) > 1:
            raise ValidationError('Há estoques duplicados para este produto. Corrija o cadastro antes de movimentar.')
        if legacy_stocks:
            if Produto.objects.filter(nome=product.nome).count() > 1:
                raise ValidationError('Há produtos com o mesmo nome. Vincule o estoque ao produto pelo cadastro antes de movimentar.')
            product_stock = legacy_stocks[0]
            product_stock.produto_catalogo = product
            product_stock.save(update_fields=['produto_catalogo'])
        else:
            product_stock = Estoque.objects.create(
                produto_catalogo=product, produto=product.nome,
                descricao=product.descricao or '', quantidade=product.estoque_atual,
                valor_unitario=unit_price, estoque_minimo=max(product.estoque_minimo, 0),
            )
    return product_stock


def update_stock_balance(stock_id, quantity_difference, entry_difference):
    from spi.models import Estoque, Produto

    # Uma atualização condicional impede saldo negativo, inclusive em concorrência.
    updated_records = Estoque.objects.filter(
        pk=stock_id, quantidade__gte=max(-quantity_difference, 0),
        entrada__gte=max(-entry_difference, 0),
    ).update(
        quantidade=F('quantidade') + quantity_difference,
        entrada=F('entrada') + entry_difference,
    )
    if not updated_records:
        raise ValidationError('Saldo insuficiente para realizar esta movimentação ou estorno.')
    product_stock = Estoque.objects.get(pk=stock_id)
    if product_stock.produto_catalogo_id:
        Produto.objects.filter(pk=product_stock.produto_catalogo_id).update(
            estoque_atual=product_stock.quantidade,
        )


def synchronize_record_movement(record, previous_record):
    from spi.models import Entrada, MovimentacaoEstoque, Produto

    is_entry = isinstance(record, Entrada)
    if is_entry:
        product_id = record.produto_id
    else:
        product_id = Produto.objects.filter(codigo_barras=record.codigo_produto).values_list('pk', flat=True).first()
        if product_id is None:
            raise ValidationError('Informe o código de barras de um produto cadastrado.')

    product = Produto.objects.select_for_update().get(pk=product_id)
    unit_price = record.preco_custo if is_entry else record.valor_unitario
    product_stock = find_or_create_product_stock(product, unit_price)
    source_field = 'entrada_origem' if is_entry else 'saida_origem'
    movement = MovimentacaoEstoque.objects.filter(**{source_field: record}).first()

    # Registros anteriores à automação já podem estar incluídos no saldo inicial.
    # Ao editar um registro antigo, contabilizamos apenas a diferença de quantidade.
    if movement is None and previous_record is not None:
        previous_product_id = previous_record.produto_id if is_entry else Produto.objects.filter(
            codigo_barras=previous_record.codigo_produto,
        ).values_list('pk', flat=True).first()
        if previous_product_id != product_id:
            raise ValidationError('Não é possível trocar o produto de uma movimentação anterior à automação.')
        previous_quantity = previous_record.quantidade if is_entry else previous_record.quantidade_saida
        quantity = record.quantidade if is_entry else record.quantidade_saida
        quantity_difference = quantity - previous_quantity
        update_stock_balance(product_stock.pk, quantity_difference if is_entry else -quantity_difference, 0)
        return

    if movement is None:
        movement = MovimentacaoEstoque(**{source_field: record})
    movement.estoque = product_stock
    movement.tipo = 'ENTRADA' if is_entry else 'SAIDA'
    movement.quantidade = record.quantidade if is_entry else record.quantidade_saida
    movement.observacao = f'{"Entrada" if is_entry else "Saída"} #{record.pk}'
    movement.save()


def save_record_and_synchronize_stock(record, save_original, *args, **kwargs):
    # Se qualquer etapa falhar, nem o registro nem o saldo são alterados.
    with transaction.atomic():
        previous_record = type(record).objects.select_for_update().filter(pk=record.pk).first() if record.pk else None
        save_original(*args, **kwargs)
        record.refresh_from_db()
        synchronize_record_movement(record, previous_record)
