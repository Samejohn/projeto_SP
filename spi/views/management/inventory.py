"""Views responsáveis por descartes e pelo inventário."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from spi.forms import DescarteForm, InventarioForm
from spi.models import Descarte, Inventario

from .helpers import delete_record, render_searchable_list


@login_required
@permission_required("spi.view_descarte", raise_exception=True)
def list_discards(request):
    discard_records = Descarte.objects.select_related("produto", "usuario").order_by(
        "-data_descarte"
    )
    return render_searchable_list(
        request,
        discard_records,
        (
            "produto__nome",
            "motivo",
            "observacao",
            "usuario__username",
            "usuario__first_name",
            "usuario__last_name",
        ),
        "management/discard_list.html",
        "discards",
    )


@login_required
@permission_required("spi.add_descarte", raise_exception=True)
def create_discard(request):
    submitted_data = request.POST if request.method == "POST" else None
    discard_form = DescarteForm(submitted_data)
    if request.method == "POST" and discard_form.is_valid():
        discard_form.save()
        messages.success(request, "Descarte cadastrado com sucesso.")
        return redirect("discard_list")
    return render(
        request,
        "management/discard_form.html",
        {"form": discard_form, "object": None},
    )


@login_required
@permission_required("spi.change_descarte", raise_exception=True)
def update_discard(request, discard_id):
    discard_record = get_object_or_404(Descarte, id=discard_id)
    submitted_data = request.POST if request.method == "POST" else None
    discard_form = DescarteForm(submitted_data, instance=discard_record)
    if request.method == "POST" and discard_form.is_valid():
        discard_form.save()
        messages.success(request, "Descarte atualizado com sucesso.")
        return redirect("discard_list")
    return render(
        request,
        "management/discard_form.html",
        {"form": discard_form, "object": discard_record},
    )


@login_required
@permission_required("spi.delete_descarte", raise_exception=True)
def delete_discard(request, discard_id):
    discard_record = get_object_or_404(Descarte, id=discard_id)
    return delete_record(
        request,
        discard_record,
        "descarte",
        "discard_list",
        "Descarte excluído com sucesso.",
    )


@login_required
@permission_required("spi.view_inventario", raise_exception=True)
def list_inventory(request):
    inventory_records = Inventario.objects.all()
    return render_searchable_list(
        request,
        inventory_records,
        (
            "numero_patrimonio",
            "id_ativo",
            "item_modelo",
            "serie_licenca",
            "setor",
            "usuario__username",
        ),
        "management/inventory_list.html",
        "inventory",
    )


@login_required
@permission_required("spi.add_inventario", raise_exception=True)
def create_inventory(request):
    submitted_data = request.POST if request.method == "POST" else None
    inventory_form = InventarioForm(submitted_data)

    if request.method == "POST" and inventory_form.is_valid():
        inventory_form.save()
        messages.success(request, "Item cadastrado no inventário com sucesso.")
        return redirect("inventory_list")

    return render(
        request,
        "management/inventory_form.html",
        {"form": inventory_form, "object": None},
    )
