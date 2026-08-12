"""Views de produtos, valores de produtos e produtos de pedidos."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from spi.forms import (
    ManagedProductForm,
    ManagedProdutoPedidoForm,
    ManagedValorProdutoForm,
)
from spi.models import ControleData, Produto, ProdutoPedido, ValorProduto

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
        ("nome", "codigo_barras", "responsavel_cadastro__username"),
        "management/product_list.html",
        "products",
    )


@login_required
@permission_required("spi.add_produto", raise_exception=True)
def create_product(request):
    submitted_data = request.POST if request.method == "POST" else None
    product_form = ManagedProductForm(submitted_data)

    if request.method == "POST" and product_form.is_valid():
        with transaction.atomic():
            product_record = product_form.save(commit=False)
            product_record.responsavel_cadastro = request.user
            product_record.controle_data = ControleData.objects.create(
                usuario_cadastro=request.user,
                usuario_atualizacao=request.user,
            )
            product_record.save()
        messages.success(request, "Produto cadastrado com sucesso.")
        return redirect("product_list")

    return render(
        request,
        "management/product_form.html",
        {"form": product_form, "object": None},
    )


@login_required
@permission_required("spi.change_produto", raise_exception=True)
def update_product(request, product_id):
    product_record = get_object_or_404(Produto, id=product_id)
    submitted_data = request.POST if request.method == "POST" else None
    product_form = ManagedProductForm(submitted_data, instance=product_record)

    if request.method == "POST" and product_form.is_valid():
        with transaction.atomic():
            updated_product = product_form.save()
            control_data = updated_product.controle_data
            control_data.usuario_atualizacao = request.user
            control_data.save(update_fields=("usuario_atualizacao", "data_atualizacao"))
        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("product_list")

    return render(
        request,
        "management/product_form.html",
        {"form": product_form, "object": product_record},
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
        ManagedProdutoPedidoForm,
        "produto_pedido_list",
        "Produto do pedido cadastrado com sucesso.",
        "Cadastrar produto do pedido",
        "Dados do produto do pedido",
        "Salvar produto do pedido",
    )


@login_required
@permission_required("spi.change_produtopedido", raise_exception=True)
def update_order_product(request, order_product_id):
    order_product_record = get_object_or_404(ProdutoPedido, id=order_product_id)
    return render_catalog_form(
        request,
        ManagedProdutoPedidoForm,
        "produto_pedido_list",
        "Produto do pedido atualizado com sucesso.",
        "Editar produto do pedido",
        "Dados do produto do pedido",
        "Salvar produto do pedido",
        database_record=order_product_record,
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
