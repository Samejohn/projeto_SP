"""Views de estoque, movimentações de estoque e alertas."""

from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from spi.forms import ManagedEstoqueForm, ManagedMovimentacaoEstoqueForm
from spi.models import Estoque, MovimentacaoEstoque

from .helpers import delete_record, render_catalog_form, render_searchable_list


# ==========================================
# ESTOQUE
# ==========================================

@login_required
@permission_required("spi.view_estoque", raise_exception=True)
def list_stock(request):
    stock_records = Estoque.objects.all().order_by("produto")

    return render_searchable_list(
        request,
        stock_records,
        (
            "produto",
            "descricao",
            "localizacao",
        ),
        "management/estoque_list.html",
        "estoque",
    )


@login_required
@permission_required("spi.add_estoque", raise_exception=True)
def create_stock(request):
    return render_catalog_form(
        request,
        ManagedEstoqueForm,
        "estoque_list",
        "Item de estoque cadastrado com sucesso.",
        "Cadastrar item de estoque",
        "Dados do estoque",
        "Salvar estoque",
        template_name="management/estoque_form.html",
    )


@login_required
@permission_required("spi.change_estoque", raise_exception=True)
def update_stock(request, stock_id):
    stock_record = get_object_or_404(Estoque, id=stock_id)
    return render_catalog_form(
        request,
        ManagedEstoqueForm,
        "estoque_list",
        "Item de estoque atualizado com sucesso.",
        "Editar item de estoque",
        "Dados do estoque",
        "Salvar estoque",
        database_record=stock_record,
        template_name="management/estoque_form.html",
    )


@login_required
@permission_required("spi.delete_estoque", raise_exception=True)
def delete_stock(request, stock_id):
    stock_record = get_object_or_404(Estoque, id=stock_id)
    return delete_record(
        request,
        stock_record,
        "item de estoque",
        "estoque_list",
        "Item de estoque excluído com sucesso.",
    )


# ==========================================
# MOVIMENTAÇÕES
# ==========================================

@login_required
@permission_required("spi.view_movimentacaoestoque", raise_exception=True)
def list_movements(request):
    movement_records = MovimentacaoEstoque.objects.select_related(
        "estoque"
    ).order_by("-data")

    return render_searchable_list(
        request,
        movement_records,
        (
            "estoque__produto",
            "tipo",
            "observacao",
        ),
        "management/movimentacoes_list.html",
        "movimentacoes_estoque",
    )


@login_required
@permission_required("spi.add_movimentacaoestoque", raise_exception=True)
def create_movement(request):
    return render_catalog_form(
        request,
        ManagedMovimentacaoEstoqueForm,
        "list_movements",
        "Movimentação de estoque registrada com sucesso.",
        "Registrar movimentação",
        "Dados da movimentação",
        "Salvar movimentação",
        template_name="management/movimentacao_form.html",
    )


# ==========================================
# ALERTAS JSON
# ==========================================

@login_required
@permission_required("spi.view_estoque", raise_exception=True)
def stock_alert_json(request):
    alert_items = Estoque.objects.filter(
        quantidade__lte=models.F("estoque_minimo")
    ).order_by("produto")

    data = [
        {
            "id": item.id,
            "produto": str(item.produto),
            "quantidade": item.quantidade,
            "estoque_minimo": item.estoque_minimo,
        }
        for item in alert_items
    ]

    return JsonResponse({"alertas": data})