from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F  # <-- NOVO IMPORT
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from spi.forms import SignInForm, SignUpForm
from spi.models import Produto, ProdutoPedido

from .management import (
    create_discard,
    create_group,
    create_inventory,
    create_link,
    create_order_product,
    create_product,
    create_product_from_modal,
    create_product_value,
    create_supplier,
    create_supplier_from_product,
    create_user,
    delete_discard,
    delete_group,
    delete_link,
    delete_order_product,
    delete_product,
    delete_product_value,
    delete_supplier,
    delete_user,
    list_discards,
    list_groups,
    list_inventory,
    list_links,
    list_order_products,
    list_product_values,
    list_products,
    list_suppliers,
    list_users,
    update_discard,
    update_group,
    update_link,
    update_order_product,
    update_product,
    update_product_value,
    update_supplier,
    update_user,
)


@login_required
def dashboard(request):
    # Produtos cujo estoque atual está no mínimo ou abaixo dele
    produtos_em_alerta = Produto.objects.filter(
        estoque_atual__lte=F("estoque_minimo")
    )

    # Quantidade de produtos em alerta
    total_produtos_alerta = produtos_em_alerta.count()

    dashboard_context = {
        "total_produtos": Produto.objects.count(),
        "total_produtos_pendentes": ProdutoPedido.objects.filter(
            status="PENDENTE"
        ).count(),
        "total_produtos_alerta": total_produtos_alerta,
        "produtos_em_alerta": produtos_em_alerta,
    }

    return render(request, "index.html", dashboard_context)


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    submitted_data = request.POST if request.method == "POST" else None
    authentication_form = SignInForm(request, data=submitted_data)
    requested_destination = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST" and authentication_form.is_valid():
        authenticated_user = authentication_form.get_user()
        login(request, authenticated_user)

        destination_is_safe = url_has_allowed_host_and_scheme(
            requested_destination,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        if destination_is_safe:
            return redirect(requested_destination)
        return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))

    return render(
        request,
        "registration/signin.html",
        {"form": authentication_form, "next": requested_destination},
    )


@require_POST
def sign_out(request):
    logout(request)
    return redirect(resolve_url(settings.LOGOUT_REDIRECT_URL))


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    submitted_data = request.POST if request.method == "POST" else None
    signup_form = SignUpForm(submitted_data)
    if request.method == "POST" and signup_form.is_valid():
        registered_user = signup_form.save()
        login(request, registered_user)
        messages.success(request, "Conta criada com sucesso. Bem-vindo ao SPI!")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": signup_form})


ERROR_CONTENT = {
    400: ("Requisição inválida", "Não conseguimos processar os dados enviados."),
    401: ("Autenticação necessária", "Entre com sua conta para acessar este conteúdo."),
    403: ("Acesso negado", "Você não tem permissão para acessar esta página."),
    404: ("Página não encontrada", "O endereço informado não existe ou foi movido."),
    500: ("Erro interno", "Encontramos uma falha inesperada. Tente novamente em instantes."),
    503: ("Serviço indisponível", "O sistema está temporariamente indisponível para manutenção."),
}


def _render_error(request, status_code):
    error_title, error_description = ERROR_CONTENT[status_code]
    error_context = {
        "status_code": status_code,
        "error_title": error_title,
        "error_description": error_description,
    }
    return render(request, "error.html", error_context, status=status_code)


def error_preview(request, status_code):
    if status_code not in ERROR_CONTENT:
        return HttpResponseNotFound("Código de erro não suportado.")
    return _render_error(request, status_code)


def bad_request(request, exception):
    return _render_error(request, 400)


def permission_denied(request, exception):
    return _render_error(request, 403)


def page_not_found(request, exception):
    return _render_error(request, 404)


def server_error(request):
    return _render_error(request, 500)