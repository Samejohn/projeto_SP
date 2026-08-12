"""Views de produtos, valores de produtos e produtos de pedidos."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from spi.forms import (
    ManagedFornecedorForm,
    ManagedLinkForm,
    ManagedOrderProductCreateForm,
    ManagedProductForm,
    ManagedProductSelectionForm,
    ManagedProductValueAmountForm,
    ManagedProdutoPedidoForm,
    ManagedValorProdutoForm,
)
from spi.models import ControleData, Link, Produto, ProdutoPedido, ValorProduto

from .helpers import delete_record, render_catalog_form, render_searchable_list


@login_required
@permission_required("spi.view_produto", raise_exception=True)
def list_products(request):
    product_records = Produto.objects.select_related(
        "responsavel_cadastro", "controle_data"
    ).order_by("nome")
    return render_searchable_list(
        request,
        product_records,
        (
            "nome",
            "codigo_barras",
            "responsavel_cadastro__username",
        ),
        "management/product_list.html",
        "products",
    )


@login_required
@permission_required(
    ("spi.add_produto", "spi.add_link", "spi.add_valorproduto"),
    raise_exception=True,
)
def create_product(request):
    submitted_data = request.POST if request.method == "POST" else None
    product_selection_form = ManagedProductSelectionForm(submitted_data)
    link_form = ManagedLinkForm(submitted_data, prefix="link")
    product_value_form = ManagedProductValueAmountForm(
        submitted_data,
        prefix="value",
    )

    if request.method == "POST":
        submitted_forms_are_valid = all(
            (
                product_selection_form.is_valid(),
                link_form.is_valid(),
                product_value_form.is_valid(),
            )
        )
    else:
        submitted_forms_are_valid = False

    if submitted_forms_are_valid:
        with transaction.atomic():
            selected_product = product_selection_form.cleaned_data["produto"]

            link_record = link_form.save(commit=False)
            link_record.controle_data = ControleData.objects.create(
                usuario_cadastro=request.user,
                usuario_atualizacao=request.user,
            )
            link_record.save()

            product_value_record = product_value_form.save(commit=False)
            product_value_record.produto = selected_product
            product_value_record.link = link_record
            product_value_record.controle_data = ControleData.objects.create(
                usuario_cadastro=request.user,
                usuario_atualizacao=request.user,
            )
            product_value_record.save()
        messages.success(request, "Link e valor cadastrados para o produto com sucesso.")
        return redirect("product_list")

    return render(
        request,
        "management/product_form.html",
        {
            "form": product_selection_form,
            "product_selection_form": product_selection_form,
            "link_form": link_form,
            "product_value_form": product_value_form,
            "new_product_form": ManagedProductForm(),
            "supplier_form": ManagedFornecedorForm(),
            "object": None,
        },
    )


@require_POST
@login_required
@permission_required("spi.add_produto", raise_exception=True)
def create_product_from_modal(request):
    """Cadastra um produto pelo modal e o devolve para o seletor da tela."""
    product_form = ManagedProductForm(request.POST)
    if not product_form.is_valid():
        return JsonResponse(
            {"success": False, "errors": product_form.errors.get_json_data()},
            status=400,
        )

    with transaction.atomic():
        product_record = product_form.save(commit=False)
        product_record.responsavel_cadastro = request.user
        product_record.controle_data = ControleData.objects.create(
            usuario_cadastro=request.user,
            usuario_atualizacao=request.user,
        )
        product_record.save()

    return JsonResponse(
        {
            "success": True,
            "product": {
                "id": product_record.id,
                "name": product_record.nome,
                "barcode": product_record.codigo_barras,
            },
        },
        status=201,
    )


@login_required
@permission_required(
    ("spi.change_produto", "spi.change_link", "spi.change_valorproduto"),
    raise_exception=True,
)
def update_product(request, product_id):
    product_record = get_object_or_404(Produto, id=product_id)
    product_value_record = product_record.valores.select_related(
        "link", "link__fornecedor"
    ).first()
    link_record = product_value_record.link if product_value_record else None
    submitted_data = request.POST if request.method == "POST" else None
    product_form = ManagedProductForm(submitted_data, instance=product_record)
    link_form = ManagedLinkForm(
        submitted_data,
        instance=link_record,
        prefix="link",
    )
    product_value_form = ManagedProductValueAmountForm(
        submitted_data,
        instance=product_value_record,
        prefix="value",
    )

    if request.method == "POST":
        submitted_forms_are_valid = all(
            (
                product_form.is_valid(),
                link_form.is_valid(),
                product_value_form.is_valid(),
            )
        )
    else:
        submitted_forms_are_valid = False

    if submitted_forms_are_valid:
        with transaction.atomic():
            updated_product = product_form.save()
            product_control_data = updated_product.controle_data
            product_control_data.usuario_atualizacao = request.user
            product_control_data.save(
                update_fields=("usuario_atualizacao", "data_atualizacao")
            )

            updated_link = link_form.save(commit=False)
            if link_record is None:
                updated_link.controle_data = ControleData.objects.create(
                    usuario_cadastro=request.user,
                    usuario_atualizacao=request.user,
                )
            else:
                link_control_data = updated_link.controle_data
                link_control_data.usuario_atualizacao = request.user
                link_control_data.save(
                    update_fields=("usuario_atualizacao", "data_atualizacao")
                )
            updated_link.save()

            updated_product_value = product_value_form.save(commit=False)
            updated_product_value.produto = updated_product
            updated_product_value.link = updated_link
            if product_value_record is None:
                updated_product_value.controle_data = ControleData.objects.create(
                    usuario_cadastro=request.user,
                    usuario_atualizacao=request.user,
                )
            else:
                value_control_data = updated_product_value.controle_data
                value_control_data.usuario_atualizacao = request.user
                value_control_data.save(
                    update_fields=("usuario_atualizacao", "data_atualizacao")
                )
            updated_product_value.save()

        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("product_list")

    return render(
        request,
        "management/product_form.html",
        {
            "form": product_form,
            "link_form": link_form,
            "product_value_form": product_value_form,
            "supplier_form": ManagedFornecedorForm(),
            "object": product_record,
        },
    )


@login_required
@permission_required("spi.delete_produto", raise_exception=True)
def delete_product(request, product_id):
    product_record = get_object_or_404(Produto, id=product_id)
    return delete_record(
        request,
        product_record,
        "produto",
        "product_list",
        "Produto excluído com sucesso.",
    )


@login_required
@permission_required("spi.view_valorproduto", raise_exception=True)
def list_product_values(request):
    product_value_records = ValorProduto.objects.select_related(
        "produto", "link", "link__fornecedor", "controle_data"
    ).order_by("-controle_data__data_cadastro")
    return render_searchable_list(
        request,
        product_value_records,
        (
            "produto__nome",
            "produto__codigo_barras",
            "link__nome",
            "link__fornecedor__nome_fornecedor",
        ),
        "management/valor_produto_list.html",
        "valores_produtos",
    )


@login_required
@permission_required("spi.add_valorproduto", raise_exception=True)
def create_product_value(request):
    return render_catalog_form(
        request,
        ManagedValorProdutoForm,
        "valor_produto_list",
        "Valor de produto cadastrado com sucesso.",
        "Cadastrar valor de produto",
        "Dados do valor",
        "Salvar valor",
    )


@login_required
@permission_required("spi.change_valorproduto", raise_exception=True)
def update_product_value(request, product_value_id):
    product_value_record = get_object_or_404(ValorProduto, id=product_value_id)
    return render_catalog_form(
        request,
        ManagedValorProdutoForm,
        "valor_produto_list",
        "Valor de produto atualizado com sucesso.",
        "Editar valor de produto",
        "Dados do valor",
        "Salvar valor",
        database_record=product_value_record,
    )


@login_required
@permission_required("spi.delete_valorproduto", raise_exception=True)
def delete_product_value(request, product_value_id):
    product_value_record = get_object_or_404(ValorProduto, id=product_value_id)
    return delete_record(
        request,
        product_value_record,
        "valor de produto",
        "valor_produto_list",
        "Valor de produto excluído com sucesso.",
    )


@login_required
@permission_required("spi.view_produtopedido", raise_exception=True)
def list_order_products(request):
    order_product_records = ProdutoPedido.objects.select_related(
        "produto", "controle_data"
    ).order_by("-controle_data__data_cadastro")
    return render_searchable_list(
        request,
        order_product_records,
        ("nome", "descricao", "status", "produto__nome", "produto__codigo_barras"),
        "management/produto_pedido_list.html",
        "produtos_pedidos",
    )


@login_required
@permission_required("spi.add_produtopedido", raise_exception=True)
def create_order_product(request):
    return render_catalog_form(
        request,
        ManagedOrderProductCreateForm,
        "produto_pedido_list",
        "Pedido de produto cadastrado com sucesso.",
        "Cadastrar pedido de produto",
        "Dados do pedido de produto",
        "Salvar pedido de produto",
        template_name="management/order_product_form.html",
    )


@login_required
@permission_required("spi.change_produtopedido", raise_exception=True)
def update_order_product(request, order_product_id):
    order_product_record = get_object_or_404(ProdutoPedido, id=order_product_id)
    return render_catalog_form(
        request,
        ManagedProdutoPedidoForm,
        "produto_pedido_list",
        "Pedido de produto atualizado com sucesso.",
        "Editar pedido de produto",
        "Dados do pedido de produto",
        "Salvar pedido de produto",
        database_record=order_product_record,
        template_name="management/order_product_form.html",
    )


@login_required
@permission_required("spi.delete_produtopedido", raise_exception=True)
def delete_order_product(request, order_product_id):
    order_product_record = get_object_or_404(ProdutoPedido, id=order_product_id)
    return delete_record(
        request,
        order_product_record,
        "produto do pedido",
        "produto_pedido_list",
        "Produto do pedido excluído com sucesso.",
    )
