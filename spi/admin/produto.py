from django.contrib import admin
from spi.models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome_produto", "preco_atual", "link_produto", "quantidade_produto")
    search_fields = ("nome_produto",)
