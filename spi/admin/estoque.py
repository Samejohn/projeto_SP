from django.db import admin 
from spi.models import Estoque, MovimentacaoEstoque 

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'produto',
        'quantidade',
        'entrada',
        'valor_unitario',
        'estoque_minimo',
        'responsavel',
        'data',
    )

    search_fields = (
        'produto',
        'descricao',
        'responsavel',
    )

    list_filter = (
        'data',
    )

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("estoque", "tipo", "quantidade", "valor_unitario", "total", "data_movimentacao", "responsavel")
    search_fields = ("estoque__nome", "responsavel__username")
    list_select_related = ("estoque", "responsavel")

