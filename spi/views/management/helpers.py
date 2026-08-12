"""Funções auxiliares compartilhadas pelas views da área de gestão."""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect, render

from spi.models import ControleData


ITEMS_PER_PAGE = 20


def render_searchable_list(
    request,
    database_records,
    search_fields,
    template_name,
    context_list_name,
):
    """Filtra, pagina e renderiza uma listagem da área de gestão."""
    search_query = request.GET.get("q", "").strip()
    filtered_records = database_records

    if search_query:
        combined_search_filter = Q()
        for search_field in search_fields:
            combined_search_filter |= Q(**{f"{search_field}__icontains": search_query})
        filtered_records = database_records.filter(combined_search_filter)

    records_paginator = Paginator(filtered_records, ITEMS_PER_PAGE)
    current_page = records_paginator.get_page(request.GET.get("page"))
    template_context = {
        context_list_name: current_page.object_list,
        "page_obj": current_page,
        "paginator": records_paginator,
        "is_paginated": records_paginator.num_pages > 1,
        "search_query": search_query,
    }
    return render(request, template_name, template_context)


def render_catalog_form(
    request,
    form_class,
    success_route_name,
    success_message,
    form_title,
    section_title,
    submit_label,
    database_record=None,
    template_name="management/catalog_form.html",
):
    """Processa formulários que possuem dados de controle de criação e edição."""
    submitted_data = request.POST if request.method == "POST" else None
    record_form = form_class(submitted_data, instance=database_record)

    if request.method == "POST" and record_form.is_valid():
        with transaction.atomic():
            saved_record = record_form.save(commit=False)

            if database_record is None:
                saved_record.controle_data = ControleData.objects.create(
                    usuario_cadastro=request.user,
                    usuario_atualizacao=request.user,
                )
            else:
                control_data = saved_record.controle_data
                control_data.usuario_atualizacao = request.user
                control_data.save(
                    update_fields=("usuario_atualizacao", "data_atualizacao")
                )

            saved_record.save()
            record_form.save_m2m()

        messages.success(request, success_message)
        return redirect(success_route_name)

    template_context = {
        "form": record_form,
        "object": database_record,
        "form_title": form_title,
        "section_title": section_title,
        "cancel_url_name": success_route_name,
        "submit_label": submit_label,
    }
    return render(request, template_name, template_context)


def delete_record(
    request,
    database_record,
    record_label,
    success_route_name,
    success_message,
    protected_message=None,
):
    """Exibe a confirmação e exclui um registro após um envio POST."""
    if request.method == "POST":
        try:
            database_record.delete()
        except ProtectedError:
            messages.error(
                request,
                protected_message
                or "Este registro não pode ser excluído porque está sendo utilizado.",
            )
        else:
            messages.success(request, success_message)
        return redirect(success_route_name)

    template_context = {
        "object": database_record,
        "object_label": record_label,
        "cancel_url_name": success_route_name,
    }
    return render(request, "management/confirm_delete.html", template_context)
