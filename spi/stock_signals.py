from django.db.models.signals import pre_delete
from django.dispatch import receiver

from spi.models import Entrada, Estoque, MovimentacaoEstoque, Produto, SaidaProduto
from spi.stock_automation import update_stock_balance


@receiver(pre_delete, sender=MovimentacaoEstoque)
def reverse_deleted_movement_balance(sender, instance, **kwargs):
    # O Django executa as exclusões e este estorno na mesma transação.
    update_stock_balance(
        instance.estoque_id,
        -instance.quantidade if instance.tipo == 'ENTRADA' else instance.quantidade,
        -instance.quantidade if instance.tipo == 'ENTRADA' else 0,
    )


@receiver(pre_delete, sender=Entrada)
@receiver(pre_delete, sender=SaidaProduto)
def reverse_legacy_record_balance(sender, instance, **kwargs):
    # Registros antigos não possuem a movimentação criada pela automação.
    is_entry_record = isinstance(instance, Entrada)
    source_field = 'entrada_origem' if is_entry_record else 'saida_origem'
    if MovimentacaoEstoque.objects.filter(**{source_field: instance}).exists():
        return  # O sinal da movimentação fará o estorno, sem duplicá-lo.
    product = instance.produto if is_entry_record else Produto.objects.filter(
        codigo_barras=instance.codigo_produto,
    ).first()
    if product is None:
        return
    product_stock = Estoque.objects.filter(produto_catalogo=product).first()
    if product_stock is None:
        return
    quantity = instance.quantidade if is_entry_record else instance.quantidade_saida
    update_stock_balance(product_stock.pk, -quantity if is_entry_record else quantity, 0)
