"""Views de estoque, movimentações de estoque e alertas."""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from spi.forms import ManagedEstoqueForm, ManagedMovimentacaoEstoqueForm
from .entry import render_entry_form
from spi.models import Estoque, MovimentacaoEstoque

from .helpers import delete_record, render_catalog_form, render_searchable_list


# ==========================================
# ESTOQUE
# ==========================================

def filter_stock_by_registration_period(stock_records, requested_period):
    """Filtra pela data de cadastro e devolve o período válido selecionado."""
    period_duration_days = {"hoje": 1, "7": 7, "15": 15, "30": 30}
    if requested_period not in period_duration_days:
        # Sem filtro ou com um valor inválido, mostramos todos os registros.
        return stock_records, ""

    current_date = timezone.localdate()
    # Hoje já conta como um dia: o período de 7 dias começa há 6 dias.
    registration_start_date = current_date - timedelta(
        days=period_duration_days[requested_period] - 1
    )
    filtered_stock_records = stock_records.filter(
        data__range=(registration_start_date, current_date)
    )
    return filtered_stock_records, requested_period


@login_required
@permission_required("spi.view_estoque", raise_exception=True)
def list_stock(request):
    stock_records = Estoque.objects.all().order_by("produto")
    # Aplicamos o período antes da busca e da paginação para manter os totais corretos.
    stock_records, selected_period = filter_stock_by_registration_period(
        stock_records, request.GET.get("periodo", "")
    )

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
        extra_context={"selected_period": selected_period},
    )


@login_required
@permission_required("spi.add_estoque", raise_exception=True)
def create_stock(request):
    return render_stock_form(
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
    return render_stock_form(
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


def render_stock_form(request, form_class, success_route_name, success_message,
                      form_title, section_title, submit_label,
                      database_record=None, template_name="management/estoque_form.html"):
    form = form_class(request.POST if request.method == "POST" else None,
                      instance=database_record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(success_route_name)
    return render(request, template_name, {
        "form": form, "object": database_record,
        "page_title": form_title, "card_title": section_title,
        "submit_button_label": submit_label, "cancel_url_name": success_route_name,
    })


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
    return render_entry_form(
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
