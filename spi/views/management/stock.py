from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

from spi.forms.management import EstoqueForm, ManagedOrderProductCreateForm, MovimentacaoEstoqueForm
from spi.models.estoque import Estoque, MovimentacaoEstoque
from spi.views.management.helpers import render_catalog_form

#Lista todos os itens do estoque com suporte a busca e alerta.
class EstoqueListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Estoque
    permission_required = 'spi.view_estoque'
    template_name = 'management/estoque_list.html'
    context_object_name = 'estoque_list'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('responsavel_cadastro')
        
        # Filtro por busca de texto
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(nome__icontains=q)
        
        # Filtro de alerta
        alerta = self.request.GET.get('alerta')
        if alerta == '1':
            queryset = queryset.filter(quantidade_estoque__lte=models.F('estoque_minimo'))
        
        # Filtro de status
        ativo = self.request.GET.get('ativo')
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_itens'] = Estoque.objects.count()
        context['itens_alerta'] = Estoque.objects.filter(
            quantidade_estoque__lte=models.F('estoque_minimo')
        ).count()
        return context

#Cadastro de um novo item no estoque.
class EstoqueCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Estoque
    permission_required = 'spi.add_estoque'
    form_class = EstoqueForm
    template_name = 'management/estoque_form.html'
    success_url = reverse_lazy('stock:estoque_list')
    success_message = 'Item cadastrado no estoque com sucesso!'

    def form_valid(self, form):
        form.instance.responsavel_cadastro = self.request.user
        return super().form_valid(form)

#Exibe detalhes do item e o histórico de movimentações.
class EstoqueDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Estoque
    permission_required = 'spi.view_estoque'
    template_name = 'management/estoque_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimentacoes'] = (
            self.object.movimentacoes
            .select_related('responsavel')
            .order_by('-data_movimentacao')[:20]
        )
        return context

#Atualiza os detalhes de um item do estoque.
class EstoqueUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Estoque
    permission_required = 'spi.change_estoque'
    form_class = EstoqueForm
    template_name = 'management/estoque_form.html'
    context_object_name = 'item'
    success_url = reverse_lazy('stock:estoque_list')
    success_message = 'Item atualizado com sucesso!'

#Remove (desativa) um item do estoque.
class EstoqueDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Estoque
    permission_required = 'spi.delete_estoque'
    template_name = 'management/estoque_confirm_delete.html'
    success_url = reverse_lazy('stock:estoque_list')
    success_message = 'Item removido com sucesso!'

    def delete(self, request, *args, **kwargs):
        # Desativa o item em vez de deletar
        self.object = self.get_object()
        self.object.ativo = False
        self.object.save()
        messages.success(request, self.success_message)
        return redirect(self.success_url)

#Registra uma nova Entrada ou Saída no estoque.
class MovimentacaoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = MovimentacaoEstoque
    permission_required = 'spi.add_movimentacaoestoque'
    form_class = MovimentacaoEstoqueForm
    template_name = 'management/movimentacao_form.html'
    success_url = reverse_lazy('stock:estoque_list')
    success_message = 'Movimentação registrada com sucesso!'

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        estoque_id = self.request.GET.get('estoque_id')
        if estoque_id:
            initial['estoque'] = estoque_id
        return initial

#Exibe o histórico geral de movimentações.
class MovimentacaoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MovimentacaoEstoque
    permission_required = 'spi.view_movimentacaoestoque'
    template_name = 'management/movimentacao_list.html'
    context_object_name = 'movimentacoes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('estoque', 'responsavel')
        
        # Filtros adicionais
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        estoque_id = self.request.GET.get('estoque')
        if estoque_id:
            queryset = queryset.filter(estoque_id=estoque_id)
        
        return queryset

# FUNÇÕES-BASE 
#listar estoque
@login_required
@permission_required("spi.view_estoque", raise_exception=True)
def list_stock(request):
    view = EstoqueListView.as_view()
    return view(request)


# criar estoque
@login_required
@permission_required('spi.add_estoque', raise_exception=True)
def create_stock(request):
    if request.method == 'POST':
        form = EstoqueForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.responsavel_cadastro = request.user
            item.save()
            messages.success(request, 'Item cadastrado no estoque com sucesso!')
            return redirect('estoque_list')
    else:
        form = EstoqueForm()

    context = {
        'form': form,
        'form_title': 'Cadastrar Produto em Estoque',
        'section_title': 'Informações do Produto no Estoque',
        'submit_label': 'Salvar',
        'cancel_url_name': 'estoque_list',
    }
    return render(request, 'management/estoque_form.html', context)

#editar estoque
@login_required
@permission_required('spi.change_estoque', raise_exception=True)
def update_stock(request, stock_id):
    estoque = get_object_or_404(Estoque, pk=stock_id)

    if request.method == 'POST':
        form = EstoqueForm(
            request.POST,
            instance=estoque
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Produto do estoque atualizado com sucesso!'
            )

            return redirect('estoque_list')

    else:
        form = EstoqueForm(
            instance=estoque
        )

    context = {
        'form': form,
        'form_title': 'Editar Produto em Estoque',
        'section_title': 'Informações do Produto no Estoque',
        'submit_label': 'Atualizar',
        'cancel_url_name': 'estoque_list',
    }

    return render(
        request,
        'management/estoque_form.html',
        context
    )

#deletar estoque
@login_required
@permission_required("spi.delete_estoque", raise_exception=True)
def delete_stock(request, stock_id):
    estoque = get_object_or_404(
        Estoque,
        pk=stock_id
    )

    if request.method == "POST":
        estoque.ativo = False

        estoque.save(
            update_fields=[
                "ativo",
                "data_atualizacao",
            ]
        )

        messages.success(
            request,
            f'O produto "{estoque.nome}" foi desativado com sucesso.'
        )

        return redirect("estoque_list")

    context = {
        "object": estoque,
        "object_label": "produto do estoque",
        "cancel_url_name": "estoque_list",
    }

    return render(
        request,
        "management/confirm_delete.html",
        context
    )
#listar movimentações
@login_required
@permission_required('spi.view_movimentacaoestoque', raise_exception=True)
def list_movements(request):
    return MovimentacaoListView.as_view()(request)

@login_required
@permission_required('spi.add_movimentacaoestoque', raise_exception=True)
def create_movement(request):
    return MovimentacaoCreateView.as_view()(request)


# API / UTILIDADES
#verificar alertas de estoque mínimo
@login_required
@permission_required('spi.view_estoque', raise_exception=True)
def estoque_alerta_json(request):
    itens_alerta = Estoque.objects.filter(
        quantidade_estoque__lte=models.F('estoque_minimo')
    ).values('id', 'nome', 'quantidade_estoque', 'estoque_minimo')
    
    return JsonResponse({
        'count': itens_alerta.count(),
        'itens': list(itens_alerta)
    })
