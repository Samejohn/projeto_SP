from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from spi.models import Produto
from spi.models import Descarte
from spi.models import Inventario


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
        fields = ("nome_produto", "link_produto", "preco_atual", "quantidade_produto",)
        labels = {
            "nome_produto": "Nome do produto",
            "link_produto": "Link do produto",
            "preco_atual": "Preço atual",
            "quantidade_produto": "Quantidade do produto"
        }
        widgets = {
            "link_produto": forms.URLInput(attrs={"placeholder": "https://exemplo.com/produto"}),
            "preco_atual": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantidade_produto": forms.NumberInput( attrs={"min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()


#Descarte

class DescarteForm(forms.ModelForm):

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

#INVENTÁRIO
class InventarioForm(forms.ModelForm):

    class Meta:
        model = Inventario
        fields = "__all__"  # Inclui todos os campos do model inventario

        # Opcional: Personalização de rótulos (labels)
        labels = {
            "motivo": "Motivo do inventario",
            "data_inventario": "Data do inventario",
        }

        # Opcional: Personalização de widgets/HTML
        widgets = {
            "data_inventario": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "motivo": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }
