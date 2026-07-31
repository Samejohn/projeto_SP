from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from spi.models import ControleData, Fornecedor, Link, Produto, ProdutoPedido, ValorProduto


class DashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="dashboard",
            email="dashboard@example.com",
            password="senha-segura",
        )
        self.client.force_login(self.user)

    def test_dashboard_displays_product_totals(self):
        for index in range(3):
            controle = ControleData.objects.create(
                usuario_cadastro=self.user,
                usuario_atualizacao=self.user,
            )
            produto = Produto.objects.create(
                nome=f"Produto {index}",
                codigo_barras=f"78900000010{index}",
                responsavel_cadastro=self.user,
                controle_data=controle,
            )
            ProdutoPedido.objects.create(
                nome=f"Pedido {index}",
                produto=produto,
                quantidade_produto=1,
                status="PENDENTE" if index < 2 else "APROVADO",
                controle_data=controle,
            )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_produtos"], 3)
        self.assertEqual(response.context["total_produtos_pendentes"], 2)
        self.assertContains(response, "<strong>3</strong>", html=True)
        self.assertContains(response, "<strong>2</strong>", html=True)


class ProductManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="gestor",
            email="gestor@example.com",
            password="senha-segura",
        )
        self.client.force_login(self.user)

    def test_create_product_records_responsible_user_and_control_data(self):
        response = self.client.post(
            reverse("product_create"),
            {"nome": "Produto de teste", "codigo_barras": "789000000001"},
        )

        self.assertRedirects(response, reverse("product_list"))
        product = Produto.objects.get(codigo_barras="789000000001")
        self.assertEqual(product.responsavel_cadastro, self.user)
        self.assertEqual(product.controle_data.usuario_cadastro, self.user)
        self.assertEqual(product.controle_data.usuario_atualizacao, self.user)

    def test_update_product_records_user_who_updated_it(self):
        controle_data = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        product = Produto.objects.create(
            nome="Nome inicial",
            codigo_barras="789000000002",
            responsavel_cadastro=self.user,
            controle_data=controle_data,
        )

        response = self.client.post(
            reverse("product_update", args=(product.pk,)),
            {"nome": "Nome atualizado", "codigo_barras": product.codigo_barras},
        )

        self.assertRedirects(response, reverse("product_list"))
        product.refresh_from_db()
        product.controle_data.refresh_from_db()
        self.assertEqual(product.nome, "Nome atualizado")
        self.assertEqual(product.controle_data.usuario_atualizacao, self.user)

    def test_product_list_displays_new_fields(self):
        controle_data = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        Produto.objects.create(
            nome="Produto listado",
            codigo_barras="789000000003",
            responsavel_cadastro=self.user,
            controle_data=controle_data,
        )

        response = self.client.get(reverse("product_list"))

        self.assertContains(response, "Produto listado")
        self.assertContains(response, "789000000003")
        self.assertContains(response, "gestor")


class CatalogManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="administrador",
            email="administrador@example.com",
            password="senha-segura",
        )
        self.client.force_login(self.user)
        controle_produto = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        self.produto = Produto.objects.create(
            nome="Notebook",
            codigo_barras="789100000001",
            responsavel_cadastro=self.user,
            controle_data=controle_produto,
        )

    def test_product_order_default_status_is_pending(self):
        controle = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        produto_pedido = ProdutoPedido.objects.create(
            nome="Pedido com status inicial",
            descricao="",
            produto=self.produto,
            quantidade_produto=1,
            controle_data=controle,
        )

        self.assertEqual(produto_pedido.status, "PENDENTE")
        self.assertEqual(produto_pedido.get_status_display(), "Pendente")

    def test_create_and_list_catalog_records(self):
        response = self.client.post(
            reverse("fornecedor_create"),
            {
                "nome_fornecedor": "Fornecedor teste",
                "cnpj_cnpj": "00.000.000/0001-00",
                "telefone_fornecedor": "(82) 99999-0000",
                "responsavel_forncedor": "Maria",
            },
        )
        self.assertRedirects(response, reverse("fornecedor_list"))
        fornecedor = Fornecedor.objects.get(cnpj_cnpj="00.000.000/0001-00")
        self.assertEqual(fornecedor.controle_data.usuario_cadastro, self.user)

        response = self.client.post(
            reverse("link_create"),
            {
                "nome": "Página do notebook",
                "url": "https://example.com/notebook",
                "fornecedor": fornecedor.pk,
            },
        )
        self.assertRedirects(response, reverse("link_list"))
        link = Link.objects.get(nome="Página do notebook")

        response = self.client.post(
            reverse("valor_produto_create"),
            {"produto": self.produto.pk, "link": link.pk, "valor": "3499.90"},
        )
        self.assertRedirects(response, reverse("valor_produto_list"))
        self.assertTrue(ValorProduto.objects.filter(produto=self.produto, link=link).exists())

        response = self.client.post(
            reverse("produto_pedido_create"),
            {
                "nome": "Notebook para desenvolvimento",
                "descricao": "Equipamento da equipe técnica",
                "produto": self.produto.pk,
                "quantidade_produto": 2,
                "status": "PENDENTE",
            },
        )
        self.assertRedirects(response, reverse("produto_pedido_list"))
        produto_pedido = ProdutoPedido.objects.get(produto=self.produto)
        self.assertEqual(produto_pedido.status, "PENDENTE")

        pages_and_content = (
            ("fornecedor_list", "Fornecedor teste"),
            ("link_list", "Página do notebook"),
            ("valor_produto_list", "3.499,90"),
            ("produto_pedido_list", "Notebook para desenvolvimento"),
        )
        for route, content in pages_and_content:
            with self.subTest(route=route):
                self.assertContains(self.client.get(reverse(route)), content)

        response = self.client.post(
            reverse("fornecedor_delete", args=(fornecedor.pk,)),
            follow=True,
        )
        self.assertContains(response, "possui links vinculados")
        self.assertTrue(Fornecedor.objects.filter(pk=fornecedor.pk).exists())

    def test_update_records_user_in_control_data(self):
        controle = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        fornecedor = Fornecedor.objects.create(
            nome_fornecedor="Nome inicial",
            cnpj_cnpj="00.000.000/0002-00",
            telefone_fornecedor="(82) 3333-0000",
            responsavel_forncedor="João",
            controle_data=controle,
        )
        editor = get_user_model().objects.create_superuser(
            username="editor",
            email="editor@example.com",
            password="senha-segura",
        )
        self.client.force_login(editor)

        response = self.client.post(
            reverse("fornecedor_update", args=(fornecedor.pk,)),
            {
                "nome_fornecedor": "Nome atualizado",
                "cnpj_cnpj": fornecedor.cnpj_cnpj,
                "telefone_fornecedor": fornecedor.telefone_fornecedor,
                "responsavel_forncedor": fornecedor.responsavel_forncedor,
            },
        )

        self.assertRedirects(response, reverse("fornecedor_list"))
        fornecedor.refresh_from_db()
        fornecedor.controle_data.refresh_from_db()
        self.assertEqual(fornecedor.nome_fornecedor, "Nome atualizado")
        self.assertEqual(fornecedor.controle_data.usuario_cadastro, self.user)
        self.assertEqual(fornecedor.controle_data.usuario_atualizacao, editor)

    def test_delete_unreferenced_records(self):
        controle = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        fornecedor = Fornecedor.objects.create(
            nome_fornecedor="Fornecedor removível",
            cnpj_cnpj="00.000.000/0003-00",
            telefone_fornecedor="(82) 3333-0001",
            responsavel_forncedor="Ana",
            controle_data=controle,
        )

        response = self.client.post(reverse("fornecedor_delete", args=(fornecedor.pk,)))

        self.assertRedirects(response, reverse("fornecedor_list"))
        self.assertFalse(Fornecedor.objects.filter(pk=fornecedor.pk).exists())
