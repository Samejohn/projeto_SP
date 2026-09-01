from django.db import admin 
from spi.models import Estoque, MovimentacaoEstoque 

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ("nome", "quantidade_estoque", "estoque_minimo", "responsavel_cadastro", "data_criacao")
    search_fields = ("nome", "descricao", "responsavel_cadastro__username")
    list_select_related = ("responsavel_cadastro",)

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("estoque", "tipo", "quantidade", "valor_unitario", "total", "data_movimentacao", "responsavel")
    search_fields = ("estoque__nome", "responsavel__username")
    list_select_related = ("estoque", "responsavel")

