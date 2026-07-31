
from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('entrar/', views.SignInView.as_view(), name='login'),
    path('cadastro/', views.signup, name='signup'),
    path('sair/', views.SignOutView.as_view(), name='logout'),
    path('erro/<int:status_code>/', views.error_preview, name='error_preview'),
    path('gestao/usuarios/', views.UserListView.as_view(), name='user_list'),
    path('gestao/usuarios/cadastrar/', views.UserCreateView.as_view(), name='user_create'),
    path('gestao/usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
    path('gestao/usuarios/<int:pk>/excluir/', views.UserDeleteView.as_view(), name='user_delete'),
    path('gestao/grupos/', views.GroupListView.as_view(), name='group_list'),
    path('gestao/grupos/cadastrar/', views.GroupCreateView.as_view(), name='group_create'),
    path('gestao/grupos/<int:pk>/editar/', views.GroupUpdateView.as_view(), name='group_update'),
    path('gestao/grupos/<int:pk>/excluir/', views.GroupDeleteView.as_view(), name='group_delete'),
    #PRODUTOS
    path('gestao/produtos/', views.ProductListView.as_view(), name='product_list'),
    path('gestao/produtos/cadastrar/', views.ProductCreateView.as_view(), name='product_create'),
    path('gestao/produtos/<int:pk>/editar/', views.ProductUpdateView.as_view(), name='product_update'),
    path('gestao/produtos/<int:pk>/excluir/', views.ProductDeleteView.as_view(), name='product_delete'),
    #FORNECEDORES
    path('gestao/fornecedores/', views.FornecedorListView.as_view(), name='fornecedor_list'),
    path('gestao/fornecedores/cadastrar/', views.FornecedorCreateView.as_view(), name='fornecedor_create'),
    path('gestao/fornecedores/<int:pk>/editar/', views.FornecedorUpdateView.as_view(), name='fornecedor_update'),
    path('gestao/fornecedores/<int:pk>/excluir/', views.FornecedorDeleteView.as_view(), name='fornecedor_delete'),
    #LINKS
    path('gestao/links/', views.LinkListView.as_view(), name='link_list'),
    path('gestao/links/cadastrar/', views.LinkCreateView.as_view(), name='link_create'),
    path('gestao/links/<int:pk>/editar/', views.LinkUpdateView.as_view(), name='link_update'),
    path('gestao/links/<int:pk>/excluir/', views.LinkDeleteView.as_view(), name='link_delete'),
    #VALORES DE PRODUTOS
    path('gestao/valores-produtos/', views.ValorProdutoListView.as_view(), name='valor_produto_list'),
    path('gestao/valores-produtos/cadastrar/', views.ValorProdutoCreateView.as_view(), name='valor_produto_create'),
    path('gestao/valores-produtos/<int:pk>/editar/', views.ValorProdutoUpdateView.as_view(), name='valor_produto_update'),
    path('gestao/valores-produtos/<int:pk>/excluir/', views.ValorProdutoDeleteView.as_view(), name='valor_produto_delete'),
    #PRODUTOS DE PEDIDOS
    path('gestao/produtos-pedidos/', views.ProdutoPedidoListView.as_view(), name='produto_pedido_list'),
    path('gestao/produtos-pedidos/cadastrar/', views.ProdutoPedidoCreateView.as_view(), name='produto_pedido_create'),
    path('gestao/produtos-pedidos/<int:pk>/editar/', views.ProdutoPedidoUpdateView.as_view(), name='produto_pedido_update'),
    path('gestao/produtos-pedidos/<int:pk>/excluir/', views.ProdutoPedidoDeleteView.as_view(), name='produto_pedido_delete'),
    #DESCARTES
    path('gestao/descarte/', views.DiscardListView.as_view(), name='discard_list'),
    path('gestao/descarte/cadastrar/', views.DiscardCreateView.as_view(), name='discard_create'),
    path('gestao/descarte/<int:pk>/editar/', views.DiscardUpdateView.as_view(), name='discard_update'),
    path('gestao/descarte/<int:pk>/excluir/', views.DiscardDeleteView.as_view(), name='discard_delete'),
    #INVENTÁRIO
    path('gestao/inventario/', views.InventoryListView.as_view(), name='inventory_list'),

]
