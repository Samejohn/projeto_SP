
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
    path('gestao/produtos/', views.ProductListView.as_view(), name='product_list'),
    path('gestao/produtos/cadastrar/', views.ProductCreateView.as_view(), name='product_create'),
    path('gestao/produtos/<int:pk>/editar/', views.ProductUpdateView.as_view(), name='product_update'),
    path('gestao/produtos/<int:pk>/excluir/', views.ProductDeleteView.as_view(), name='product_delete'),

]
