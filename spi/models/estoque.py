from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Estoque(models.Model):
    produto_catalogo = models.OneToOneField(
        "spi.Produto", on_delete=models.PROTECT, null=True, blank=True,
        related_name="saldo_estoque", verbose_name="Produto do catálogo",
    )
    produto = models.CharField(
        max_length=150,
        verbose_name='Produto'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    quantidade = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade em estoque'
    )
    entrada = models.PositiveIntegerField(
        default=0,
        verbose_name='Entrada'
    )
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Unitário'
    )
    estoque_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque Mínimo'
    )
    responsavel = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Responsável'
    )
    localizacao = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Localização'
    )
    data = models.DateField(
        auto_now_add=True,
        verbose_name='Data'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['produto']
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return self.produto

    def save(self, *args, **kwargs):
        from spi.models import Produto

        with transaction.atomic():
            super().save(*args, **kwargs)
            # Ajustes manuais no controle também devem aparecer no catálogo.
            if self.produto_catalogo_id:
                Produto.objects.filter(pk=self.produto_catalogo_id).update(
                    estoque_atual=self.quantidade,
                )

    @property
    def total(self):
        if self.quantidade and self.valor_unitario:
            return self.quantidade * self.valor_unitario
        return Decimal('0.00')


class MovimentacaoEstoque(models.Model):
    entrada_origem = models.OneToOneField(
        "spi.Entrada", on_delete=models.CASCADE, null=True, blank=True,
        related_name="movimentacao_automatica", editable=False,
    )
    saida_origem = models.OneToOneField(
        "spi.SaidaProduto", on_delete=models.CASCADE, null=True, blank=True,
        related_name="movimentacao_automatica", editable=False,
    )
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.estoque.produto} ({self.quantidade})"

    def save(self, *args, **kwargs):
        from spi.stock_automation import update_stock_balance

        if self.quantidade <= 0 or self.tipo not in dict(self.TIPO_CHOICES):
            raise ValidationError('Informe uma quantidade positiva e um tipo válido.')
        with transaction.atomic():
            previous_movement = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
            # Estorna o valor anterior antes de aplicar uma edição. A transação
            # desfaz ambas as operações se o novo saldo não for válido.
            if previous_movement and previous_movement.estoque_id == self.estoque_id:
                previous_balance_effect = previous_movement.quantidade if previous_movement.tipo == 'ENTRADA' else -previous_movement.quantidade
                new_balance_effect = self.quantidade if self.tipo == 'ENTRADA' else -self.quantidade
                update_stock_balance(
                    self.estoque_id, new_balance_effect - previous_balance_effect,
                    (self.quantidade if self.tipo == 'ENTRADA' else 0) - (previous_movement.quantidade if previous_movement.tipo == 'ENTRADA' else 0),
                )
                super().save(*args, **kwargs)
                return
            if previous_movement:
                previous_quantity = previous_movement.quantidade
                update_stock_balance(
                    previous_movement.estoque_id,
                    -previous_quantity if previous_movement.tipo == 'ENTRADA' else previous_quantity,
                    -previous_quantity if previous_movement.tipo == 'ENTRADA' else 0,
                )
            update_stock_balance(
                self.estoque_id,
                self.quantidade if self.tipo == 'ENTRADA' else -self.quantidade,
                self.quantidade if self.tipo == 'ENTRADA' else 0,
            )
            super().save(*args, **kwargs)
