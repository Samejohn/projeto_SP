from django.contrib import admin
from spi.models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "cpf_cnpj",
        "telefone",
        "responsavel",
        "ativo",
    )

    list_filter = ("ativo",)

    search_fields = (
        "nome",
        "cpf_cnpj",
        "responsavel",
    )

    ordering = ("nome",)