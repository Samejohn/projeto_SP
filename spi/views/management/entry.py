from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from spi.models.entrada import Entrada
from spi.forms.management import EntradaForm

def list_entry(request):
    entradas = Entrada.objects.all()
    return render(request, "management/entrada_list.html", {"entradas": entradas})


def create_entry(request):
    if request.method == "POST":
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            if request.user.is_authenticated:
                entrada.usuario = request.user
            entrada.save()

            # Atualiza o saldo do estoque associado
            produto = entrada.produto
            produto.quantidade += entrada.quantidade
            produto.save()

            messages.success(request, "Entrada registrada com sucesso!")
            return redirect("entrada_list")
    else:
        form = EntradaForm()

    return render(request, "management/entrada_form.html", {"form": form, "title": "Cadastrar Entrada"})


def update_entry(request, entry_id):
    entrada = get_object_or_404(Entrada, id=entry_id)
    qtd_antiga = entrada.quantidade

    if request.method == "POST":
        form = EntradaForm(request.POST, instance=entrada)
        if form.is_valid():
            nova_entrada = form.save()

            # Ajusta a diferença de quantidade no produto
            diferenca = nova_entrada.quantidade - qtd_antiga
            produto = nova_entrada.produto
            produto.quantidade += diferenca
            produto.save()

            messages.success(request, "Entrada atualizada com sucesso!")
            return redirect("entrada_list")
    else:
        form = EntradaForm(instance=entrada)

    return render(request, "management/entrada_form.html", {"form": form, "title": "Editar Entrada"})


def delete_entry(request, entry_id):
    entrada = get_object_or_404(Entrada, id=entry_id)

    if request.method == "POST":
        # Subtrai do produto a quantidade que havia entrado
        produto = entrada.produto
        produto.quantidade -= entrada.quantidade
        produto.save()

        entrada.delete()
        messages.success(request, "Entrada removida com sucesso!")
        return redirect("entrada_list")

    return render(request, "management/entrada_confirm_delete.html", {"entrada": entrada})