from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("entrar/", views.sign_in, name="login"),
    path("cadastro/", views.signup, name="signup"),
    path("sair/", views.sign_out, name="logout"),
    path("erro/<int:status_code>/", views.error_preview, name="error_preview"),

    # Usuários
    path("gestao/usuarios/", views.list_users, name="user_list"),
    path("gestao/usuarios/cadastrar/", views.create_user, name="user_create"),
    path("gestao/usuarios/<int:user_id>/editar/", views.update_user, name="user_update"),
    path("gestao/usuarios/<int:user_id>/excluir/", views.delete_user, name="user_delete"),

    # Grupos
    path("gestao/grupos/", views.list_groups, name="group_list"),
    path("gestao/grupos/cadastrar/", views.create_group, name="group_create"),
    path("gestao/grupos/<int:group_id>/editar/", views.update_group, name="group_update"),
    path("gestao/grupos/<int:group_id>/excluir/", views.delete_group, name="group_delete"),

    # Produtos
    path("gestao/produtos/", views.list_products, name="product_list"),
    path("gestao/produtos/cadastrar/", views.create_product, name="product_create"),
    path(
        "gestao/produtos/cadastrar-no-modal/",
        views.create_product_from_modal,
        name="product_create_from_modal",
    ),
    path("gestao/produtos/<int:product_id>/editar/", views.update_product, name="product_update"),
    path("gestao/produtos/<int:product_id>/excluir/", views.delete_product, name="product_delete"),

    # Fornecedores
    path("gestao/fornecedores/", views.list_suppliers, name="fornecedor_list"),
    path("gestao/fornecedores/cadastrar/", views.create_supplier, name="fornecedor_create"),
    path(
        "gestao/fornecedores/cadastrar-no-produto/",
        views.create_supplier_from_product,
        name="supplier_create_from_product",
    ),
    path("gestao/fornecedores/<int:supplier_id>/editar/", views.update_supplier, name="fornecedor_update"),
    path("gestao/fornecedores/<int:supplier_id>/excluir/", views.delete_supplier, name="fornecedor_delete"),

    # Links
    path("gestao/links/", views.list_links, name="link_list"),
    path("gestao/links/cadastrar/", views.create_link, name="link_create"),
    path("gestao/links/<int:link_id>/editar/", views.update_link, name="link_update"),
    path("gestao/links/<int:link_id>/excluir/", views.delete_link, name="link_delete"),

    # Valores de produtos
    path("gestao/valores-produtos/", views.list_product_values, name="valor_produto_list"),
    path("gestao/valores-produtos/cadastrar/", views.create_product_value, name="valor_produto_create"),
    path("gestao/valores-produtos/<int:product_value_id>/editar/", views.update_product_value, name="valor_produto_update"),
    path("gestao/valores-produtos/<int:product_value_id>/excluir/", views.delete_product_value, name="valor_produto_delete"),

    # Produtos de pedidos
    path("gestao/produtos-pedidos/", views.list_order_products, name="produto_pedido_list"),
    path("gestao/produtos-pedidos/cadastrar/", views.create_order_product, name="produto_pedido_create"),
    path("gestao/produtos-pedidos/<int:order_product_id>/editar/", views.update_order_product, name="produto_pedido_update"),
    path("gestao/produtos-pedidos/<int:order_product_id>/excluir/", views.delete_order_product, name="produto_pedido_delete"),

    # Descartes
    path("gestao/descarte/", views.list_discards, name="discard_list"),
    path("gestao/descarte/cadastrar/", views.create_discard, name="discard_create"),
    path("gestao/descarte/<int:discard_id>/editar/", views.update_discard, name="discard_update"),
    path("gestao/descarte/<int:discard_id>/excluir/", views.delete_discard, name="discard_delete"),

    # Inventário
    path("gestao/inventario/", views.list_inventory, name="inventory_list"),
    path("gestao/inventario/cadastrar/", views.create_inventory, name="inventory_create"),
]
