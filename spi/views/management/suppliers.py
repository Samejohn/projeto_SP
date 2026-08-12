"""Views responsáveis por fornecedores e seus links."""

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404

from spi.forms import ManagedFornecedorForm, ManagedLinkForm
from spi.models import Fornecedor, Link

from .helpers import delete_record, render_catalog_form, render_searchable_list


@login_required
@permission_required("spi.view_fornecedor", raise_exception=True)
def list_suppliers(request):
    supplier_records = Fornecedor.objects.select_related("controle_data").order_by(
        "nome_fornecedor"
    )
    return render_searchable_list(
        request,
        supplier_records,
        (
            "nome_fornecedor",
            "cnpj_cnpj",
            "telefone_fornecedor",
            "responsavel_forncedor",
        ),
        "management/fornecedor_list.html",
        "fornecedores",
    )


@login_required
@permission_required("spi.add_fornecedor", raise_exception=True)
def create_supplier(request):
    return render_catalog_form(
        request,
        ManagedFornecedorForm,
        "fornecedor_list",
        "Fornecedor cadastrado com sucesso.",
        "Cadastrar fornecedor",
        "Dados do fornecedor",
        "Salvar fornecedor",
    )


@login_required
@permission_required("spi.change_fornecedor", raise_exception=True)
def update_supplier(request, supplier_id):
    supplier_record = get_object_or_404(Fornecedor, id=supplier_id)
    return render_catalog_form(
        request,
        ManagedFornecedorForm,
        "fornecedor_list",
        "Fornecedor atualizado com sucesso.",
        "Editar fornecedor",
        "Dados do fornecedor",
        "Salvar fornecedor",
        database_record=supplier_record,
    )


@login_required
@permission_required("spi.delete_fornecedor", raise_exception=True)
def delete_supplier(request, supplier_id):
    supplier_record = get_object_or_404(Fornecedor, id=supplier_id)
    return delete_record(
        request,
        supplier_record,
        "fornecedor",
        "fornecedor_list",
        "Fornecedor excluído com sucesso.",
        "O fornecedor não pode ser excluído porque possui links vinculados.",
    )


@login_required
@permission_required("spi.view_link", raise_exception=True)
def list_links(request):
    link_records = Link.objects.select_related("fornecedor", "controle_data").order_by("nome")
    return render_searchable_list(
        request,
        link_records,
        ("nome", "url", "fornecedor__nome_fornecedor", "fornecedor__cnpj_cnpj"),
        "management/link_list.html",
        "links",
    )


@login_required
@permission_required("spi.add_link", raise_exception=True)
def create_link(request):
    return render_catalog_form(
        request,
        ManagedLinkForm,
        "link_list",
        "Link cadastrado com sucesso.",
        "Cadastrar link",
        "Dados do link",
        "Salvar link",
    )


@login_required
@permission_required("spi.change_link", raise_exception=True)
def update_link(request, link_id):
    link_record = get_object_or_404(Link, id=link_id)
    return render_catalog_form(
        request,
        ManagedLinkForm,
        "link_list",
        "Link atualizado com sucesso.",
        "Editar link",
        "Dados do link",
        "Salvar link",
        database_record=link_record,
    )


@login_required
@permission_required("spi.delete_link", raise_exception=True)
def delete_link(request, link_id):
    link_record = get_object_or_404(Link, id=link_id)
    return delete_record(
        request,
        link_record,
        "link",
        "link_list",
        "Link excluído com sucesso.",
        "O link não pode ser excluído porque possui valores de produtos vinculados.",
    )
