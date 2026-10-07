from django.contrib import admin
from spi.models.entrada import Entrada


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    # Campos exibidos na tabela do Django Admin
    list_display = (
        'id',
        'get_codigo_produto',
        'produto',
        'quantidade',
        'get_preco_custo_formatted',
        'get_total_formatted',
        'nota_fiscal',
        'ordem_fornecimento',
        'fornecedor',
        'usuario',
        'data_entrada',
    )

    # Links de acesso rápido na tabela
    list_display_links = ('id', 'produto')

    # Filtros na lateral direita
    list_filter = (
        'data_entrada',
        'fornecedor',
        'usuario',
    )

    # Campos de busca no topo
    search_fields = (
        'produto__codigo',
        'produto__descricao',
        'nota_fiscal',
        'ordem_fornecimento',
        'fornecedor',
    )

    # Otimização de consulta de chave estrangeira
    raw_id_fields = ('produto', 'usuario')

    # Ordenação padrão
    ordering = ('-data_entrada',)

    # Campos de apenas leitura no formulário do admin
    readonly_fields = ('data_entrada', 'get_total_display')

    # Organização dos campos no formulário de edição/detalhes
    fieldsets = (
        ('Informações do Produto', {
            'fields': ('produto', 'quantidade', 'preco_custo', 'get_total_display')
        }),
        ('Documentação e Origem', {
            'fields': ('nota_fiscal', 'ordem_fornecimento', 'fornecedor')
        }),
        ('Auditoria e Observações', {
            'fields': ('usuario', 'data_entrada', 'observacao')
        }),
    )

    # Preenche automaticamente o usuário logado ao criar via Admin
    def save_model(self, request, obj, form, change):
        if not change and not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    # Métodos auxiliares para exibição de colunas na tabela
    @admin.display(description='Cód. Produto', ordering='produto__codigo')
    def get_codigo_produto(self, obj):
        return getattr(obj.produto, 'codigo', obj.produto.id)

    @admin.display(description='Preço Custo')
    def get_preco_custo_formatted(self, obj):
        return f"R$ {obj.preco_custo:.2f}" if obj.preco_custo else "R$ 0,00"

    @admin.display(description='Total')
    def get_total_formatted(self, obj):
        return f"R$ {obj.total:.2f}" if obj.total else "R$ 0,00"

    @admin.display(description='Total Calculado')
    def get_total_display(self, obj):
        return f"R$ {obj.total:.2f}" if obj.total else "R$ 0,00"