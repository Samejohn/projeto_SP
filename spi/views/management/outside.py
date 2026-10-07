"""Views de saída de estoque."""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.utils import timezone

from spi.forms import SaidaProdutoForm
from spi.models import SaidaProduto

from .helpers import delete_record, render_searchable_list
from .entry import render_entry_form


# ==========================================
# SAÍDAS DE ESTOQUE
# ==========================================

def filter_exits_by_departure_period(exit_records, requested_period):
    """Filtra as saídas pela data de saída e retorna o período válido selecionado."""
    period_duration_days = {"hoje": 1, "7": 7, "15": 15, "30": 30}
    if requested_period not in period_duration_days:
        # Sem seleção ou com um valor inválido, exibimos todos os períodos.
        return exit_records, ""

    current_date = timezone.localdate()
    # Hoje é o primeiro dia: o período de 7 dias inclui hoje e os 6 anteriores.
    departure_start_date = current_date - timedelta(
        days=period_duration_days[requested_period] - 1
    )
    # Usamos o fuso local e incluímos todos os horários das datas do período.
    filtered_exit_records = exit_records.filter(
        data_hora__date__range=(departure_start_date, current_date)
    )
    return filtered_exit_records, requested_period


@login_required
@permission_required("spi.view_saidaproduto", raise_exception=True)
def list_exit(request):
    exit_records = SaidaProduto.objects.select_related("responsavel").order_by("-data_hora")
    # Aplicamos o período antes da pesquisa e da paginação para listar só as saídas desejadas.
    exit_records, selected_period = filter_exits_by_departure_period(
        exit_records, request.GET.get("periodo", "")
    )

    return render_searchable_list(
        request,
        exit_records,
        (
            "codigo_produto",
            "descricao",
            "motivo_destino",
            "setor",
        ),
        "management/saida_list.html",
        "saidas",
        extra_context={"selected_period": selected_period},
    )


@login_required
@permission_required("spi.add_saidaproduto", raise_exception=True)
def create_exit(request):
    return render_entry_form(
        request,
        SaidaProdutoForm,
        "saida_list",
        "Saída de estoque registrada com sucesso.",
        "Cadastrar saída de estoque",
        "Dados da saída",
        "Salvar saída",
        template_name="management/saida_form.html",
    )


@login_required
@permission_required("spi.change_saidaproduto", raise_exception=True)
def update_exit(request, exit_id):
    exit_record = get_object_or_404(SaidaProduto, id=exit_id)
    return render_entry_form(
        request,
        SaidaProdutoForm,
        "saida_list",
        "Saída de estoque atualizada com sucesso.",
        "Editar saída de estoque",
        "Dados da saída",
        "Salvar saída",
        database_record=exit_record,
        template_name="management/saida_form.html",
    )


@login_required
@permission_required("spi.delete_saidaproduto", raise_exception=True)
def delete_exit(request, exit_id):
    exit_record = get_object_or_404(SaidaProduto, id=exit_id)
    return delete_record(
        request,
        exit_record,
        "saída de estoque",
        "saida_list",
        "Saída de estoque excluída com sucesso.",
    )
