from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from spi.forms import SignInForm, SignUpForm

from .management import (
    GroupCreateView,
    GroupDeleteView,
    GroupListView,
    GroupUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
    DiscardListView
)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class SignInView(LoginView):
    authentication_form = SignInForm
    template_name = 'registration/signin.html'
    redirect_authenticated_user = True


class SignOutView(LogoutView):
    http_method_names = ['post', 'options']


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Conta criada com sucesso. Bem-vindo ao SPI!')
        return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form': form})


ERROR_CONTENT = {
    400: ('Requisição inválida', 'Não conseguimos processar os dados enviados.'),
    401: ('Autenticação necessária', 'Entre com sua conta para acessar este conteúdo.'),
    403: ('Acesso negado', 'Você não tem permissão para acessar esta página.'),
    404: ('Página não encontrada', 'O endereço informado não existe ou foi movido.'),
    500: ('Erro interno', 'Encontramos uma falha inesperada. Tente novamente em instantes.'),
    503: ('Serviço indisponível', 'O sistema está temporariamente indisponível para manutenção.'),
}


def _render_error(request, status_code):
    title, description = ERROR_CONTENT[status_code]
    return render(
        request,
        'error.html',
        {'status_code': status_code, 'error_title': title, 'error_description': description},
        status=status_code,
    )


def error_preview(request, status_code):
    if status_code not in ERROR_CONTENT:
        return HttpResponseNotFound('Código de erro não suportado.')
    return _render_error(request, status_code)


def bad_request(request, exception):
    return _render_error(request, 400)


def permission_denied(request, exception):
    return _render_error(request, 403)


def page_not_found(request, exception):
    return _render_error(request, 404)


def server_error(request):
    return _render_error(request, 500)
