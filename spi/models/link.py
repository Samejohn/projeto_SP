from django.db import models


class Link(models.Model):
    nome = models.CharField("Nome", max_length=255)
    url = models.URLField("URL", max_length=2048)
    fornecedor = models.ForeignKey(
        "Fornecedor",
        on_delete=models.PROTECT,
        related_name="links",
        verbose_name="Fornecedor",
    )
    controle_data = models.ForeignKey(
        "ControleData",
        on_delete=models.PROTECT,
        related_name="links",
        verbose_name="Controle de datas",
    )

    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
