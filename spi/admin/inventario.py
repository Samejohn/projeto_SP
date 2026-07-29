from django.contrib import admin
from spi.models import Inventario


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = (
        "numero_patrimonio",
        "categoria",
        "item_modelo",
        "status",
        "setor",
        "usuario",
        "data_aquisicao",
        "validade_garantia",
    )

    list_filter = (
        "categoria",
        "status",
        "setor",
        "data_aquisicao",
        "validade_garantia",
    )

    # Certifique-se de que o model Colaborador tem os campos 'nome' e 'cpf'
    search_fields = (
        "numero_patrimonio",
        "id_inventario",
        "item_modelo",
        "serie_licenca",
        "usuario__nome",
    )

    ordering = ("numero_patrimonio",)

    list_per_page = 20

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "numero_patrimonio",
                    "id_inventario",
                    "categoria",
                    "item_modelo",
                    "serie_licenca",
                )
            },
        ),
        (
            "Aquisição",
            {
                "fields": (
                    "data_aquisicao",
                    "valor",
                    "validade_garantia",
                )
            },
        ),
        (
            "Responsável",
            {
                "fields": (
                    "status",
                    "setor",
                    "usuario",
                )
            },
        ),
        (
            "Informações Adicionais",
            {
                "fields": ("observacoes",),
            },
        ),
        (
            "Controle",
            {
                "classes": ("collapse",),
                "fields": (
                    "criado_em",
                    "atualizado_em",
                ),
            },
        ),
    )
