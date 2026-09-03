from decimal import Decimal
from django.db import models


class ProdutoPedido(models.Model):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("APROVADO", "Aprovado"),
        ("COMPRADO", "Comprado"),
        ("RECEBIDO", "Recebido"),
    ]


    produto = models.ForeignKey(
            "Produto",
            on_delete=models.PROTECT,
            related_name="pedidos",
            verbose_name="Produto",
        )
    
    descricao = models.TextField("Descrição", blank=True)
    
    link = models.ForeignKey(
        "Link",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Link do produto",
        null=True,
    )
    quantidade_produto = models.PositiveIntegerField("Quantidade do produto")
    status = models.CharField(
        "Status",
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDENTE",
    )
    valor_produto = models.DecimalField(
        "Valor do produto",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    total = models.DecimalField(
        "Total",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    controle_data = models.ForeignKey(
        "ControleData",
        on_delete=models.PROTECT,
        related_name="produtos_pedidos",
        verbose_name="Controle de datas",
    )

    class Meta:
        verbose_name = "Produto do pedido"
        verbose_name_plural = "Produtos dos pedidos"
        ordering = ["-controle_data__data_cadastro"]

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_produto} un."

    def get_registered_product_value(self):
        """Obtém o valor cadastrado para a combinação de produto e link."""
        if not self.produto_id or not self.link_id:
            return None

        from .valor_produto import ValorProduto

        return ValorProduto.objects.filter(
            produto_id=self.produto_id,
            link_id=self.link_id,
        ).first()

    def save(self, *args, **kwargs):
        # Busca o valor unitário cadastrado caso valor_produto não tenha sido preenchido
        if not self.valor_produto:
            registro_valor = self.get_registered_product_value()
            if registro_valor:
                # Assumindo que a model ValorProduto possui o campo 'valor'
                self.valor_produto = registro_valor.valor

        # Calcula o Total automaticamente se o valor_produto existir
        if self.valor_produto is not None:
            qtd = Decimal(self.quantidade_produto or 0)
            unitario = Decimal(self.valor_produto)
            self.total = qtd * unitario
        else:
            self.total = Decimal("0.00")

        super().save(*args, **kwargs)