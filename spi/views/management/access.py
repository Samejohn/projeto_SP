"""Views responsáveis pelo gerenciamento de usuários e grupos."""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from spi.forms import ManagedGroupForm, ManagedUserForm

from .helpers import delete_record, render_searchable_list


@login_required
@permission_required("auth.view_user", raise_exception=True)
def list_users(request):
    user_records = get_user_model().objects.prefetch_related("groups").order_by("username")
    return render_searchable_list(
        request,
        user_records,
        ("username", "first_name", "last_name", "email"),
        "management/user_list.html",
        "users",
    )


@login_required
@permission_required("auth.add_user", raise_exception=True)
def create_user(request):
    submitted_data = request.POST if request.method == "POST" else None
    user_form = ManagedUserForm(submitted_data)

    if request.method == "POST" and user_form.is_valid():
        user_form.save()
        messages.success(request, "Usuário cadastrado com sucesso.")
        return redirect("user_list")

    return render(
        request,
        "management/user_form.html",
        {"form": user_form, "object": None},
    )


@login_required
@permission_required("auth.change_user", raise_exception=True)
def update_user(request, user_id):
    user_record = get_object_or_404(get_user_model(), id=user_id)
    if user_record.is_superuser and not request.user.is_superuser:
        raise PermissionDenied

    submitted_data = request.POST if request.method == "POST" else None
    user_form = ManagedUserForm(submitted_data, instance=user_record)

    if request.method == "POST" and user_form.is_valid():
        user_form.save()
        messages.success(request, "Usuário atualizado com sucesso.")
        return redirect("user_list")

    return render(
        request,
        "management/user_form.html",
        {"form": user_form, "object": user_record},
    )


@login_required
@permission_required("auth.delete_user", raise_exception=True)
def delete_user(request, user_id):
    user_record = get_object_or_404(get_user_model(), id=user_id)
    deleting_own_user = user_record == request.user
    deleting_superuser_without_access = user_record.is_superuser and not request.user.is_superuser
    if deleting_own_user or deleting_superuser_without_access:
        raise PermissionDenied

    return delete_record(
        request,
        user_record,
        "usuário",
        "user_list",
        "Usuário excluído com sucesso.",
    )


@login_required
@permission_required("auth.view_group", raise_exception=True)
def list_groups(request):
    group_records = Group.objects.prefetch_related("permissions").order_by("name")
    return render_searchable_list(
        request,
        group_records,
        ("name",),
        "management/group_list.html",
        "groups",
    )


@login_required
@permission_required("auth.add_group", raise_exception=True)
def create_group(request):
    submitted_data = request.POST if request.method == "POST" else None
    group_form = ManagedGroupForm(submitted_data)
    if request.method == "POST" and group_form.is_valid():
        group_form.save()
        messages.success(request, "Grupo cadastrado com sucesso.")
        return redirect("group_list")
    return render(request, "management/group_form.html", {"form": group_form, "object": None})


@login_required
@permission_required("auth.change_group", raise_exception=True)
def update_group(request, group_id):
    group_record = get_object_or_404(Group, id=group_id)
    submitted_data = request.POST if request.method == "POST" else None
    group_form = ManagedGroupForm(submitted_data, instance=group_record)
    if request.method == "POST" and group_form.is_valid():
        group_form.save()
        messages.success(request, "Grupo atualizado com sucesso.")
        return redirect("group_list")
    return render(
        request,
        "management/group_form.html",
        {"form": group_form, "object": group_record},
    )


@login_required
@permission_required("auth.delete_group", raise_exception=True)
def delete_group(request, group_id):
    group_record = get_object_or_404(Group, id=group_id)
    return delete_record(
        request,
        group_record,
        "grupo",
        "group_list",
        "Grupo excluído com sucesso.",
    )
