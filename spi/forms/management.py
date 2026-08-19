import json

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from spi.models import Descarte, Fornecedor, Inventario, Link, Produto, ProdutoPedido, ValorProduto


class BootstrapFormMixin:
    def _apply_bootstrap_classes(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = "form-select"
            else:
                css_class = "form-control"
            widget.attrs["class"] = f'{widget.attrs.get("class", "")} {css_class}'.strip()


class ManagedUserForm(BootstrapFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Na edição, deixe em branco para manter a senha atual.",
    )
    password2 = forms.CharField(
        label="Confirmação da senha",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "groups",
        )
        labels = {
            "username": "Usuário",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "is_active": "Ativo",
            "is_staff": "Acesso à administração",
            "groups": "Grupos",
        }
        widgets = {"groups": forms.SelectMultiple(attrs={"size": 8})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].queryset = Group.objects.order_by("name")
        if not self.instance.pk:
            self.fields["password1"].required = True
            self.fields["password2"].required = True
        self._apply_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "As senhas não coincidem.")
            elif password1:
                try:
                    validate_password(password1, self.instance)
                except ValidationError as error:
                    self.add_error("password1", error)
                else:
                    self.instance.set_password(password1)
        return cleaned_data


class ManagedGroupForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "permissions")
        labels = {"name": "Nome", "permissions": "Permissões"}
        widgets = {"permissions": forms.SelectMultiple(attrs={"size": 14})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].queryset = self.fields["permissions"].queryset.select_related(
            "content_type"
        ).order_by("content_type__app_label", "content_type__model", "codename")
        self._apply_bootstrap_classes()


class ManagedProductForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Produto
        fields = ("nome", "descricao", "codigo_barras")
        labels = {
            "nome": "Nome do produto",
            "descricao": "Descrição",
            "codigo_barras": "Código de barras",
        }
        widgets = {
            "codigo_barras": forms.TextInput(attrs={"placeholder": "Digite o código de barras"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get("nome")
        product_description = cleaned_data.get("descricao")
        barcode = cleaned_data.get("codigo_barras")
        if not product_name or not barcode:
            return cleaned_data

        product_with_same_identity = Produto.objects.filter(
            nome__iexact=product_name,
            descricao=product_description,
            codigo_barras=barcode,
        ).exclude(id=self.instance.id)
        if product_with_same_identity.exists():
            self.add_error(
                "codigo_barras",
                "Não é possível cadastrar: já existe um produto com este nome e código de barras.",
            )
        return cleaned_data


class ManagedProductSelectionForm(BootstrapFormMixin, forms.Form):
    produto = forms.ModelChoiceField(
        label="Cadastrar Produto",
        queryset=Produto.objects.none(),
        empty_label="Selecione um produto",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product_field = self.fields["produto"]
        product_field.queryset = Produto.objects.order_by("nome", "codigo_barras")
        product_field.label_from_instance = self._get_product_label
        self._apply_bootstrap_classes()

    @staticmethod
    def _get_product_label(product_record):
        return f"{product_record.nome} — {product_record.codigo_barras}"


#Descarte

class DescarteForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = Descarte
        fields = "__all__"  # Inclui todos os campos do model Descarte

        # Opcional: Personalização de rótulos (labels)
        labels = {
            "motivo": "Motivo do Descarte",
            "data_descarte": "Data do Descarte",
        }

        # Opcional: Personalização de widgets/HTML
        widgets = {
            "data_descarte": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "motivo": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()


class ManagedFornecedorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = (
            "nome_fornecedor",
            "cnpj_cnpj",
            "cep_fornecedor",
            "telefone_fornecedor",
            "whatsapp_fornecedor",
            "email_fornecedor",
            "responsavel_fornecedor",
        )
        labels = {
            "nome_fornecedor": "Nome do fornecedor",
            "cnpj_cnpj": "CNPJ",
            "cep_fornecedor": "CEP",
            "telefone_fornecedor": "Telefone",
            "whatsapp_fornecedor": "WhatsApp",
            "email_fornecedor": "E-mail",
            "responsavel_fornecedor": "Responsável",
        }
        widgets = {
            "cnpj_cnpj": forms.TextInput(
                attrs={"placeholder": "00.000.000/0000-00"}
            ),
            "cep_fornecedor": forms.TextInput(
                attrs={"placeholder": "00000-000"}
            ),
            "telefone_fornecedor": forms.TextInput(
                attrs={"placeholder": "(00) 00000-0000"}
            ),
            "whatsapp_fornecedor": forms.TextInput(
                attrs={"placeholder": "(00) 00000-0000"}
            ),
            "email_fornecedor": forms.EmailInput(
                attrs={"placeholder": "exemplo@dominio.com"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()


class ManagedLinkForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Link
        fields = ("nome", "url", "fornecedor")
        labels = {"nome": "Empresa E-commerce de Marketplace", "url": "URL", "fornecedor": "Fornecedor"}
        widgets = {"url": forms.URLInput(attrs={"placeholder": "https://exemplo.com/produto"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fornecedor"].queryset = Fornecedor.objects.order_by("nome_fornecedor")
        self._apply_bootstrap_classes()


class ManagedValorProdutoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ValorProduto
        fields = ("produto", "link", "valor")
        labels = {"produto": "Produto", "link": "Link", "valor": "Valor"}
        widgets = {"valor": forms.NumberInput(attrs={"min": "0", "step": "0.01"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.order_by("nome")
        self.fields["link"].queryset = Link.objects.select_related("fornecedor").order_by(
            "fornecedor__nome_fornecedor", "nome"
        )
        self._apply_bootstrap_classes()


class ProductLinkSelect(forms.Select):
    """Inclui os valores de cada produto nos atributos da opção de link."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs,
        )
        link_record = getattr(value, "instance", None)
        if link_record is not None:
            values_by_product = {}
            for product_value_record in link_record.valores_produtos.all():
                product_id = str(product_value_record.produto_id)
                values_by_product.setdefault(product_id, str(product_value_record.valor))
            option["attrs"]["data-product-values"] = json.dumps(values_by_product)
            option["attrs"]["data-supplier-name"] = (
                link_record.fornecedor.nome_fornecedor
            )
        return option


class ManagedProdutoPedidoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ProdutoPedido
        fields = (
            "nome",
            "descricao",
            "produto",
            "link",
            "quantidade_produto",
            "status",
        )
        labels = {
            "nome": "Nome do item",
            "descricao": "Descrição",
            "produto": "Produto",
            "link": "Link do produto",
            "quantidade_produto": "Quantidade",
            "status": "Status",
        }
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "quantidade_produto": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.order_by("nome")
        link_field = self.fields["link"]
        link_field.required = True
        link_field.widget = ProductLinkSelect()
        link_field.queryset = Link.objects.filter(
            valores_produtos__isnull=False
        ).select_related("fornecedor").prefetch_related(
            "valores_produtos"
        ).order_by("nome").distinct()
        link_field.label_from_instance = self._get_link_label
        self._apply_bootstrap_classes()

    @staticmethod
    def _get_link_label(link_record):
        return f"{link_record.nome} — {link_record.fornecedor.nome_fornecedor}"

    def clean(self):
        cleaned_data = super().clean()
        selected_product = cleaned_data.get("produto")
        selected_link = cleaned_data.get("link")
        if (
            selected_product
            and selected_link
            and not ValorProduto.objects.filter(
                produto=selected_product,
                link=selected_link,
            ).exists()
        ):
            self.add_error(
                "link",
                "Selecione um link pertencente ao produto informado.",
            )
        return cleaned_data


class ManagedOrderProductCreateForm(ManagedProdutoPedidoForm):
    """Cadastro de pedido sem status, utilizando o padrão definido no modelo."""

    class Meta(ManagedProdutoPedidoForm.Meta):
        fields = (
            "nome",
            "descricao",
            "produto",
            "link",
            "quantidade_produto",
        )


class ManagedProductValueAmountForm(BootstrapFormMixin, forms.ModelForm):
    """Formulário usado quando produto e link ainda serão criados juntos."""

    class Meta:
        model = ValorProduto
        fields = ("valor",)
        labels = {"valor": "Valor do produto"}
        widgets = {"valor": forms.NumberInput(attrs={"min": "0", "step": "0.01"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()


# Inventário
class InventarioForm(BootstrapFormMixin, forms.ModelForm):

    class Meta:
        model = Inventario
        fields = "__all__"

        widgets = {
            "data_aquisicao": forms.DateInput(attrs={"type": "date"}),
            "validade_garantia": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()
        for field in self.fields.values():
            field.widget.attrs["autocomplete"] = "off"

