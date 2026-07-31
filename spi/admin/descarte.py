from django.contrib import admin
from spi.models import Descarte


@admin.register(Descarte)
class DescarteAdmin(admin.ModelAdmin):
    list_display = ("produto", "quantidade", "observacao", "data_descarte")
    search_fields = ("produto__nome",)
    list_filter = ("data_descarte",)
