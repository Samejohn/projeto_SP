from django.contrib import admin
from .models import Brand, Category, Product, Patrimonio
from django.http import HttpResponse
import csv
# Register your models here.

# Registro de Marcas.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)

# Registro de Categorias.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)

# Registro de Produtos.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):  
    list_display = ('title', 'brand', 'category', 'price', 'is_active',  'created_at', 'updated_at')
    list_filter = ('is_active', 'brand', 'category')
    search_fields = ('title', 'brand__name', 'category__name')

# Função para exportar registros selecionados para Arquivos
def export_to_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['Título', 'Marca', 'Categoria', 'Preço', 'Ativo', 'Criado em', 'Atualizado em'])

    for product in queryset:
        writer.writerow([product.title, product.brand.name, product.category.name, product.price, product.is_active, product.created_at, product.updated_at])

        return response
    
    export_to_csv.short_description = 'Exportar para CSV'
    actions = [export_to_csv]

from django.contrib import admin
from .models import Patrimonio

@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'status')