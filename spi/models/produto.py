from django.conf import settings
from django.db import models

class Produto(models.Model):
    nome = models.CharField("Nome", max_length=255)
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    codigo_barras = models.CharField("Código de barras", max_length=128, unique=True)
    responsavel_cadastro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="produtos_cadastrados",
        verbose_name="Responsável pelo cadastro",
    )
    controle_data = models.ForeignKey(
        "ControleData",
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Controle de datas",
    )
    estoque_atual = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=5) # Quantidade mínima padrão

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
