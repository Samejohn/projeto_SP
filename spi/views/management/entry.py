"""Views de entrada de estoque."""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from spi.forms import EntradaForm  # Ajuste o nome do formulário se necessário
from spi.models import Entrada

from .helpers import delete_record, render_searchable_list


# ==========================================
# ENTRADAS DE ESTOQUE
# ==========================================

def filter_entries_by_receipt_period(entry_records, requested_period):
    """Filtra pela data de recebimento e retorna o período válido selecionado."""
    period_duration_days = {"hoje": 1, "7": 7, "15": 15, "30": 30}
    if requested_period not in period_duration_days:
        # Um período ausente ou inválido mantém a listagem completa.
        return entry_records, ""

    current_date = timezone.localdate()
    # Hoje conta como o primeiro dia: 7 dias incluem hoje e os 6 anteriores.
    receipt_start_date = current_date - timedelta(
        days=period_duration_days[requested_period] - 1
    )
    # A conversão para data usa o fuso local e inclui todo o último dia.
    filtered_entry_records = entry_records.filter(
        data_entrada__date__range=(receipt_start_date, current_date)
    )
    return filtered_entry_records, requested_period


@login_required
@permission_required("spi.view_entrada", raise_exception=True)
def list_entry(request):
    entry_records = Entrada.objects.select_related("produto", "usuario").order_by("-data_entrada")
    # Filtramos antes da pesquisa e da paginação para calcular os totais corretamente.
    entry_records, selected_period = filter_entries_by_receipt_period(
        entry_records, request.GET.get("periodo", "")
    )

    return render_searchable_list(
        request,
        entry_records,
        (
            "produto__codigo_barras",
            "produto__nome",
            "produto__descricao",
            "nota_fiscal",
            "ordem_fornecimento",
            "fornecedor",
        ),
        "management/entrada_list.html",
        "entradas",
        extra_context={"selected_period": selected_period},
    )


@login_required
@permission_required("spi.add_entrada", raise_exception=True)
def create_entry(request):
    return render_entry_form(
        request,
        EntradaForm,
        "entrada_list",
        "Entrada de estoque registrada com sucesso.",
        "Cadastrar entrada de estoque",
        "Dados da entrada",
        "Salvar entrada",
        template_name="management/entrada_form.html",
    )


@login_required
@permission_required("spi.change_entrada", raise_exception=True)
def update_entry(request, entry_id):
    entry_record = get_object_or_404(Entrada, id=entry_id)
    return render_entry_form(
        request,
        EntradaForm,
        "entrada_list",
        "Entrada de estoque atualizada com sucesso.",
        "Editar entrada de estoque",
        "Dados da entrada",
        "Salvar entrada",
        database_record=entry_record,
        template_name="management/entrada_form.html",
    )


def render_entry_form(request, form_class, success_route_name, success_message,
                      form_title, section_title, submit_label,
                      database_record=None, template_name="management/entrada_form.html"):
    form = form_class(request.POST if request.method == "POST" else None,
                      instance=database_record)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        if database_record is None:
            if hasattr(entry, 'usuario'):
                entry.usuario = request.user
            else:
                entry.responsavel = request.user
        try:
            entry.save()
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, success_message)
            return redirect(success_route_name)
    return render(request, template_name, {
        "form": form,
        "object": database_record,
        "page_title": form_title,
        "card_title": section_title,
        "submit_button_label": submit_label,
        "cancel_url_name": success_route_name,
    })


@login_required
@permission_required("spi.delete_entrada", raise_exception=True)
def delete_entry(request, entry_id):
    entry_record = get_object_or_404(Entrada, id=entry_id)
    return delete_record(
        request,
        entry_record,
        "entrada de estoque",
        "entrada_list",
        "Entrada de estoque excluída com sucesso.",
    )
