from django.conf import settings
from django.db import models


class ControleData(models.Model):
    data_cadastro = models.DateTimeField("Data de cadastro", auto_now_add=True)
    data_atualizacao = models.DateTimeField("Data de atualização", auto_now=True)
    usuario_cadastro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="controles_criados",
        verbose_name="Usuário do cadastro",
    )
    usuario_atualizacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="controles_atualizados",
        verbose_name="Usuário da atualização",
    )

    class Meta:
        verbose_name = "Controle de data"
        verbose_name_plural = "Controles de data"
        ordering = ["-data_atualizacao"]

    def __str__(self):
        return f"Controle #{self.pk}"
