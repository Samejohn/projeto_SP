from django.contrib import admin
from spi.models import ControleData, Fornecedor, Link, Produto, ProdutoPedido, ValorProduto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo_barras", "responsavel_cadastro", "controle_data")
    search_fields = ("nome", "codigo_barras", "responsavel_cadastro__username")
    list_select_related = ("responsavel_cadastro", "controle_data")


@admin.register(ControleData)
class ControleDataAdmin(admin.ModelAdmin):
    list_display = ("id", "data_cadastro", "data_atualizacao", "usuario_cadastro", "usuario_atualizacao")
    list_select_related = ("usuario_cadastro", "usuario_atualizacao")


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome_fornecedor", "cnpj_cnpj", "telefone_fornecedor", "responsavel_forncedor")
    search_fields = ("nome_fornecedor", "cnpj_cnpj")


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("nome", "fornecedor", "url")
    search_fields = ("nome", "fornecedor__nome_fornecedor", "url")


@admin.register(ValorProduto)
class ValorProdutoAdmin(admin.ModelAdmin):
    list_display = ("produto", "link", "valor", "controle_data")
    search_fields = ("produto__nome", "link__nome")


@admin.register(ProdutoPedido)
class ProdutoPedidoAdmin(admin.ModelAdmin):
    list_display = ("nome", "produto", "quantidade_produto", "status", "controle_data")
    search_fields = ("nome", "produto__nome")
    list_filter = ("status",)
