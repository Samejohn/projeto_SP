from django.db import models


class Fornecedor(models.Model):
    nome_fornecedor = models.CharField("Nome do fornecedor", max_length=255)
    cnpj_cnpj = models.CharField("CNPJ", max_length=18, unique=True)
    telefone_fornecedor = models.CharField("Telefone", max_length=32)
    whatsapp_fornecedor = models.CharField("WhatsApp", max_length=32)
    cep_fornecedor = models.CharField("CEP", max_length=9)
    email_fornecedor = models.EmailField("E-mail", max_length=254, blank=True, null=True)
    responsavel_fornecedor = models.CharField("Responsável", max_length=255)
    controle_data = models.ForeignKey(
        "ControleData",
        on_delete=models.PROTECT,
        related_name="fornecedores",
        verbose_name="Controle de datas",
    )

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["nome_fornecedor"]

    def __str__(self):
        return self.nome_fornecedor