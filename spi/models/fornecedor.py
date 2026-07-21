from django.db import models


class Fornecedor(models.Model):
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome"
    )

    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CPF/CNPJ"
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone"
    )

    responsavel = models.CharField(
        max_length=150,
        verbose_name="Responsável"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome