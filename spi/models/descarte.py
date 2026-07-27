from django.conf import settings
from django.db import models


class Descarte(models.Model):
    DESTINACOES = [
        ("REC", "Reciclagem"),
        ("REA", "Reaproveitamento"),
        ("DOA", "Doação"),
        ("LIX", "Lixo Comum"),
        ("RES", "Resíduo Perigoso"),
    ]

    produto = models.ForeignKey(
        "Produto",
        on_delete=models.PROTECT,
        related_name="descartes",
        verbose_name="Produto",
    )

    quantidade = models.PositiveIntegerField(
        verbose_name="Quantidade"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="descartes",
        verbose_name="Usuário",
    )

    motivo = models.CharField(
        max_length=255,
        verbose_name="Motivo do descarte",
    )

    destinacao = models.CharField(
        max_length=3,
        choices=DESTINACOES,
        default="LIX",
        verbose_name="Destinação recomendada",
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação",
    )

    data_descarte = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do descarte",
    )

    class Meta:
        verbose_name = "Descarte"
        verbose_name_plural = "Descartes"
        ordering = ["-data_descarte"]

    def __str__(self):
        return f"{self.produto} - {self.quantidade} un."