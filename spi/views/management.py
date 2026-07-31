from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from spi.forms import (
    DescarteForm,
    ManagedFornecedorForm,
    ManagedGroupForm,
    ManagedLinkForm,
    ManagedProductForm,
    ManagedProdutoPedidoForm,
    ManagedUserForm,
    ManagedValorProdutoForm,
)
from spi.models import (
    ControleData,
    Descarte,
    Fornecedor,
    Inventario,
    Link,
    Produto,
    ProdutoPedido,
    ValorProduto,
)


class ManagementPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


class SearchableListMixin:
    paginate_by = 20
    search_fields = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(filters)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class ControleDataCreateMixin:
    success_message = "Registro cadastrado com sucesso."

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.controle_data = ControleData.objects.create(
                usuario_cadastro=self.request.user,
                usuario_atualizacao=self.request.user,
            )
            response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class ControleDataUpdateMixin:
    success_message = "Registro atualizado com sucesso."

    def form_valid(self, form):
        with transaction.atomic():
            controle_data = form.instance.controle_data
            controle_data.usuario_atualizacao = self.request.user
            controle_data.save(update_fields=("usuario_atualizacao", "data_atualizacao"))
            response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class ProtectedDeleteMixin:
    success_message = "Registro excluído com sucesso."
    protected_message = "Este registro não pode ser excluído porque está sendo utilizado."

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, self.success_message)
        return response


class UserListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = get_user_model()
    permission_required = "auth.view_user"
    template_name = "management/user_list.html"
    context_object_name = "users"
    search_fields = ("username", "first_name", "last_name", "email")

    def get_queryset(self):
        return super().get_queryset().prefetch_related("groups").order_by("username")


class UserCreateView(ManagementPermissionMixin, CreateView):
    model = get_user_model()
    permission_required = "auth.add_user"
    form_class = ManagedUserForm
    template_name = "management/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        messages.success(self.request, "Usuário cadastrado com sucesso.")
        return super().form_valid(form)


class UserUpdateView(ManagementPermissionMixin, UpdateView):
    model = get_user_model()
    permission_required = "auth.change_user"
    form_class = ManagedUserForm
    template_name = "management/user_form.html"
    success_url = reverse_lazy("user_list")

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        if user.is_superuser and not self.request.user.is_superuser:
            raise PermissionDenied
        return user

    def form_valid(self, form):
        messages.success(self.request, "Usuário atualizado com sucesso.")
        return super().form_valid(form)


class UserDeleteView(ManagementPermissionMixin, DeleteView):
    model = get_user_model()
    permission_required = "auth.delete_user"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("user_list")
    extra_context = {"object_label": "usuário", "cancel_url_name": "user_list"}

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        if user == self.request.user or (user.is_superuser and not self.request.user.is_superuser):
            raise PermissionDenied
        return user

    def form_valid(self, form):
        messages.success(self.request, "Usuário excluído com sucesso.")
        return super().form_valid(form)


class GroupListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Group
    permission_required = "auth.view_group"
    template_name = "management/group_list.html"
    context_object_name = "groups"
    search_fields = ("name",)

    def get_queryset(self):
        return super().get_queryset().prefetch_related("permissions").order_by("name")


class GroupCreateView(ManagementPermissionMixin, CreateView):
    model = Group
    permission_required = "auth.add_group"
    form_class = ManagedGroupForm
    template_name = "management/group_form.html"
    success_url = reverse_lazy("group_list")

    def form_valid(self, form):
        messages.success(self.request, "Grupo cadastrado com sucesso.")
        return super().form_valid(form)


class GroupUpdateView(ManagementPermissionMixin, UpdateView):
    model = Group
    permission_required = "auth.change_group"
    form_class = ManagedGroupForm
    template_name = "management/group_form.html"
    success_url = reverse_lazy("group_list")

    def form_valid(self, form):
        messages.success(self.request, "Grupo atualizado com sucesso.")
        return super().form_valid(form)


class GroupDeleteView(ManagementPermissionMixin, DeleteView):
    model = Group
    permission_required = "auth.delete_group"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("group_list")
    extra_context = {"object_label": "grupo", "cancel_url_name": "group_list"}

    def form_valid(self, form):
        messages.success(self.request, "Grupo excluído com sucesso.")
        return super().form_valid(form)

# PRODUTOS
class ProductListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Produto
    permission_required = "spi.view_produto"
    template_name = "management/product_list.html"
    context_object_name = "products"
    search_fields = ("nome", "codigo_barras", "responsavel_cadastro__username")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "responsavel_cadastro", "controle_data"
        ).order_by("nome")


class ProductCreateView(ManagementPermissionMixin, CreateView):
    model = Produto
    permission_required = "spi.add_produto"
    form_class = ManagedProductForm
    template_name = "management/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        with transaction.atomic():
            controle_data = ControleData.objects.create(
                usuario_cadastro=self.request.user,
                usuario_atualizacao=self.request.user,
            )
            form.instance.responsavel_cadastro = self.request.user
            form.instance.controle_data = controle_data
            response = super().form_valid(form)
        messages.success(self.request, "Produto cadastrado com sucesso.")
        return response

  


class ProductUpdateView(ManagementPermissionMixin, UpdateView):
    model = Produto
    permission_required = "spi.change_produto"
    form_class = ManagedProductForm
    template_name = "management/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        with transaction.atomic():
            controle_data = form.instance.controle_data
            controle_data.usuario_atualizacao = self.request.user
            controle_data.save(update_fields=("usuario_atualizacao", "data_atualizacao"))
            response = super().form_valid(form)
        messages.success(self.request, "Produto atualizado com sucesso.")
        return response


class ProductDeleteView(ManagementPermissionMixin, DeleteView):
    model = Produto
    permission_required = "spi.delete_produto"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("product_list")
    extra_context = {"object_label": "produto", "cancel_url_name": "product_list"}

    def form_valid(self, form):
        messages.success(self.request, "Produto excluído com sucesso.")
        return super().form_valid(form)


# FORNECEDORES
class FornecedorListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Fornecedor
    permission_required = "spi.view_fornecedor"
    template_name = "management/fornecedor_list.html"
    context_object_name = "fornecedores"
    search_fields = ("nome_fornecedor", "cnpj_cnpj", "telefone_fornecedor", "responsavel_forncedor")

    def get_queryset(self):
        return super().get_queryset().select_related("controle_data").order_by("nome_fornecedor")


class FornecedorCreateView(ControleDataCreateMixin, ManagementPermissionMixin, CreateView):
    model = Fornecedor
    permission_required = "spi.add_fornecedor"
    form_class = ManagedFornecedorForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("fornecedor_list")
    success_message = "Fornecedor cadastrado com sucesso."
    extra_context = {
        "form_title": "Cadastrar fornecedor",
        "section_title": "Dados do fornecedor",
        "cancel_url_name": "fornecedor_list",
        "submit_label": "Salvar fornecedor",
    }


class FornecedorUpdateView(ControleDataUpdateMixin, ManagementPermissionMixin, UpdateView):
    model = Fornecedor
    permission_required = "spi.change_fornecedor"
    form_class = ManagedFornecedorForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("fornecedor_list")
    success_message = "Fornecedor atualizado com sucesso."
    extra_context = {
        "form_title": "Editar fornecedor",
        "section_title": "Dados do fornecedor",
        "cancel_url_name": "fornecedor_list",
        "submit_label": "Salvar fornecedor",
    }


class FornecedorDeleteView(ProtectedDeleteMixin, ManagementPermissionMixin, DeleteView):
    model = Fornecedor
    permission_required = "spi.delete_fornecedor"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("fornecedor_list")
    success_message = "Fornecedor excluído com sucesso."
    protected_message = "O fornecedor não pode ser excluído porque possui links vinculados."
    extra_context = {"object_label": "fornecedor", "cancel_url_name": "fornecedor_list"}


# LINKS
class LinkListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Link
    permission_required = "spi.view_link"
    template_name = "management/link_list.html"
    context_object_name = "links"
    search_fields = ("nome", "url", "fornecedor__nome_fornecedor", "fornecedor__cnpj_cnpj")

    def get_queryset(self):
        return super().get_queryset().select_related("fornecedor", "controle_data").order_by("nome")


class LinkCreateView(ControleDataCreateMixin, ManagementPermissionMixin, CreateView):
    model = Link
    permission_required = "spi.add_link"
    form_class = ManagedLinkForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("link_list")
    success_message = "Link cadastrado com sucesso."
    extra_context = {
        "form_title": "Cadastrar link",
        "section_title": "Dados do link",
        "cancel_url_name": "link_list",
        "submit_label": "Salvar link",
    }


class LinkUpdateView(ControleDataUpdateMixin, ManagementPermissionMixin, UpdateView):
    model = Link
    permission_required = "spi.change_link"
    form_class = ManagedLinkForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("link_list")
    success_message = "Link atualizado com sucesso."
    extra_context = {
        "form_title": "Editar link",
        "section_title": "Dados do link",
        "cancel_url_name": "link_list",
        "submit_label": "Salvar link",
    }


class LinkDeleteView(ProtectedDeleteMixin, ManagementPermissionMixin, DeleteView):
    model = Link
    permission_required = "spi.delete_link"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("link_list")
    success_message = "Link excluído com sucesso."
    protected_message = "O link não pode ser excluído porque possui valores de produtos vinculados."
    extra_context = {"object_label": "link", "cancel_url_name": "link_list"}


# VALORES DE PRODUTOS
class ValorProdutoListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = ValorProduto
    permission_required = "spi.view_valorproduto"
    template_name = "management/valor_produto_list.html"
    context_object_name = "valores_produtos"
    search_fields = ("produto__nome", "produto__codigo_barras", "link__nome", "link__fornecedor__nome_fornecedor")

    def get_queryset(self):
        return super().get_queryset().select_related(
            "produto", "link", "link__fornecedor", "controle_data"
        ).order_by("-controle_data__data_cadastro")


class ValorProdutoCreateView(ControleDataCreateMixin, ManagementPermissionMixin, CreateView):
    model = ValorProduto
    permission_required = "spi.add_valorproduto"
    form_class = ManagedValorProdutoForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("valor_produto_list")
    success_message = "Valor de produto cadastrado com sucesso."
    extra_context = {
        "form_title": "Cadastrar valor de produto",
        "section_title": "Dados do valor",
        "cancel_url_name": "valor_produto_list",
        "submit_label": "Salvar valor",
    }


class ValorProdutoUpdateView(ControleDataUpdateMixin, ManagementPermissionMixin, UpdateView):
    model = ValorProduto
    permission_required = "spi.change_valorproduto"
    form_class = ManagedValorProdutoForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("valor_produto_list")
    success_message = "Valor de produto atualizado com sucesso."
    extra_context = {
        "form_title": "Editar valor de produto",
        "section_title": "Dados do valor",
        "cancel_url_name": "valor_produto_list",
        "submit_label": "Salvar valor",
    }


class ValorProdutoDeleteView(ProtectedDeleteMixin, ManagementPermissionMixin, DeleteView):
    model = ValorProduto
    permission_required = "spi.delete_valorproduto"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("valor_produto_list")
    success_message = "Valor de produto excluído com sucesso."
    extra_context = {"object_label": "valor de produto", "cancel_url_name": "valor_produto_list"}


# PRODUTOS DE PEDIDOS
class ProdutoPedidoListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = ProdutoPedido
    permission_required = "spi.view_produtopedido"
    template_name = "management/produto_pedido_list.html"
    context_object_name = "produtos_pedidos"
    search_fields = ("nome", "descricao", "status", "produto__nome", "produto__codigo_barras")

    def get_queryset(self):
        return super().get_queryset().select_related("produto", "controle_data").order_by(
            "-controle_data__data_cadastro"
        )


class ProdutoPedidoCreateView(ControleDataCreateMixin, ManagementPermissionMixin, CreateView):
    model = ProdutoPedido
    permission_required = "spi.add_produtopedido"
    form_class = ManagedProdutoPedidoForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("produto_pedido_list")
    success_message = "Produto do pedido cadastrado com sucesso."
    extra_context = {
        "form_title": "Cadastrar produto do pedido",
        "section_title": "Dados do produto do pedido",
        "cancel_url_name": "produto_pedido_list",
        "submit_label": "Salvar produto do pedido",
    }


class ProdutoPedidoUpdateView(ControleDataUpdateMixin, ManagementPermissionMixin, UpdateView):
    model = ProdutoPedido
    permission_required = "spi.change_produtopedido"
    form_class = ManagedProdutoPedidoForm
    template_name = "management/catalog_form.html"
    success_url = reverse_lazy("produto_pedido_list")
    success_message = "Produto do pedido atualizado com sucesso."
    extra_context = {
        "form_title": "Editar produto do pedido",
        "section_title": "Dados do produto do pedido",
        "cancel_url_name": "produto_pedido_list",
        "submit_label": "Salvar produto do pedido",
    }


class ProdutoPedidoDeleteView(ProtectedDeleteMixin, ManagementPermissionMixin, DeleteView):
    model = ProdutoPedido
    permission_required = "spi.delete_produtopedido"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("produto_pedido_list")
    success_message = "Produto do pedido excluído com sucesso."
    extra_context = {"object_label": "produto do pedido", "cancel_url_name": "produto_pedido_list"}



# DESCARTES
class DiscardListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Descarte
    permission_required = "spi.view_descarte"
    template_name = "management/discard_list.html"
    context_object_name = "discards"

    search_fields = (
        "produto__nome", "motivo", "observacao", "usuario__username", "usuario__first_name", "usuario__last_name",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("produto", "usuario")
            .order_by("-data_descarte")
        )


class DiscardCreateView(ManagementPermissionMixin, CreateView):
    model = Descarte
    permission_required = "spi.add_descarte"
    form_class = DescarteForm
    template_name = "management/discard_form.html"
    success_url = reverse_lazy("discard_list")

    def form_valid(self, form):
        messages.success(self.request, "Descarte cadastrado com sucesso.")
        return super().form_valid(form)


class DiscardUpdateView(ManagementPermissionMixin, UpdateView):
    model = Descarte
    permission_required = "spi.change_descarte"
    form_class = DescarteForm
    template_name = "management/discard_form.html"
    success_url = reverse_lazy("discard_list")

    def form_valid(self, form):
        messages.success(self.request, "Descarte atualizado com sucesso.")
        return super().form_valid(form)


class DiscardDeleteView(ManagementPermissionMixin, DeleteView):
    model = Descarte
    permission_required = "spi.delete_descarte"
    template_name = "management/confirm_delete.html"
    success_url = reverse_lazy("discard_list")
    extra_context = {"object_label": "descarte", "cancel_url_name": "discard_list"}

    def form_valid(self, form):
        messages.success(self.request, "Descarte excluído com sucesso.")
        return super().form_valid(form)

#INVENTÁRIO
class InventoryListView(ManagementPermissionMixin, SearchableListMixin, ListView):
    model = Inventario
    permission_required = "spi.view_inventario"
    template_name = "management/inventory_list.html"
    context_object_name = "inventory"
    paginate_by = 20
