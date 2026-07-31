from django.db import models


class ValorProduto(models.Model):
    produto = models.ForeignKey(
        "Produto",
        on_delete=models.PROTECT,
        related_name="valores",
        verbose_name="Produto",
    )
    link = models.ForeignKey(
        "Link",
        on_delete=models.PROTECT,
        related_name="valores_produtos",
        verbose_name="Link",
    )
    valor = models.DecimalField("Valor", max_digits=12, decimal_places=2)
    controle_data = models.ForeignKey(
        "ControleData",
        on_delete=models.PROTECT,
        related_name="valores_produtos",
        verbose_name="Controle de datas",
    )

    class Meta:
        verbose_name = "Valor de produto"
        verbose_name_plural = "Valores de produtos"
        ordering = ["-controle_data__data_cadastro"]

    def __str__(self):
        return f"{self.produto} - R$ {self.valor}"
