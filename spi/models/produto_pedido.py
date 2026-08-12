from django.db import models


class ProdutoPedido(models.Model):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("APROVADO", "Aprovado"),
        ("COMPRADO", "Comprado"),
    ]

    nome = models.CharField("Nome", max_length=255)
    descricao = models.TextField("Descrição", blank=True)
    produto = models.ForeignKey(
        "Produto",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Produto",
    )
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
        return f"{self.nome} - {self.quantidade_produto} un."

    def get_registered_product_value(self):
        """Obtém o valor cadastrado para a combinação de produto e link."""
        if not self.produto_id or not self.link_id:
            return None

        from .valor_produto import ValorProduto

        return ValorProduto.objects.filter(
            produto_id=self.produto_id,
            link_id=self.link_id,
        ).first()
