from django.contrib import admin
from spi.models import SaidaProduto

@admin.register(SaidaProduto)
class SaidaProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo_produto', 'descricao', 'quantidade_saida', 'motivo_destino', 'setor', 'total', 'responsavel', 'data_hora')
    list_filter = ('motivo_destino', 'setor', 'data_hora')
    search_fields = ('codigo_produto', 'descricao', 'setor')
    readonly_fields = ('data_hora',)