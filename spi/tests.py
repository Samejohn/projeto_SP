from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from spi.models import (
    ControleData,
    Fornecedor,
    Inventario,
    Link,
    Produto,
    ProdutoPedido,
    ValorProduto,
)


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
            
            # Adicionando estoque mínimo
            estoque_minimo = 5
            estoque_atual = 3 if index < 2 else 10    # 2 produtos em alerta
            
            produto = Produto.objects.create(
                nome=f"Produto {index}",
                descricao=f"Descrição do produto {index}",
                codigo_barras=f"78900000010{index}",
                responsavel_cadastro=self.user,
                controle_data=controle,
                estoque_atual=estoque_atual,
                estoque_minimo=estoque_minimo,
            )
            
            ProdutoPedido.objects.create(
                nome=f"Pedido {index}",
                produto=produto,
                quantidade_produto=1,
                valor_produto="3499.90",
                total="6999.80",
                status="PENDENTE" if index < 2 else "APROVADO",
                controle_data=controle,
            )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_produtos"], 3)
        self.assertEqual(response.context["total_produtos_pendentes"], 2)
        self.assertEqual(response.context["total_produtos_alerta"], 2)  # NOVO TESTE
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
        supplier_control_data = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        self.supplier = Fornecedor.objects.create(
            nome_fornecedor="Fornecedor de produtos",
            cnpj_cnpj="00.000.000/0010-00",
            telefone_fornecedor="(82) 99999-0010",
            responsavel_fornecedor="Responsável",
            controle_data=supplier_control_data,
        )

    def test_create_product_records_responsible_user_and_control_data(self):
        product_response = self.client.post(
            reverse("product_create_from_modal"),
            {
                "nome": "Produto de teste",
                "descricao": "Descrição do produto de teste",
                "codigo_barras": "789000000001",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(product_response.status_code, 201)
        product = Produto.objects.get(codigo_barras="789000000001")

        response = self.client.post(
            reverse("product_create"),
            {
                "produto": product.pk,
                "link-nome": "Página do produto de teste",
                "link-url": "https://example.com/produto-teste",
                "link-fornecedor": self.supplier.pk,
                "value-valor": "125.90",
                "valor_produto": "3499.90",
                "total": "6999.80",
            },
        )

        self.assertRedirects(response, reverse("product_list"))
        self.assertEqual(product.responsavel_cadastro, self.user)
        self.assertEqual(product.controle_data.usuario_cadastro, self.user)
        self.assertEqual(product.controle_data.usuario_atualizacao, self.user)
        product_link = Link.objects.get(nome="Página do produto de teste")
        self.assertEqual(product_link.fornecedor, self.supplier)
        self.assertTrue(
            ValorProduto.objects.filter(
                produto=product,
                link=product_link,
                valor="125.90",
            ).exists()
        )

    def test_product_modal_rejects_same_name_and_barcode(self):
        first_response = self.client.post(
            reverse("product_create_from_modal"),
            {
                "nome": "Produto duplicado",
                "descricao": "Descrição do produto duplicado",
                "codigo_barras": "789000000099",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(first_response.status_code, 201)

        duplicate_response = self.client.post(
            reverse("product_create_from_modal"),
            {
                "nome": "Produto duplicado",
                "codigo_barras": "789000000099",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(duplicate_response.status_code, 400)
        error_messages = duplicate_response.json()["errors"]["codigo_barras"]
        self.assertIn(
            "Não é possível cadastrar: já existe um produto com este nome e código de barras.",
            [error["message"] for error in error_messages],
        )

    def test_product_modal_allows_same_name_with_different_barcode(self):
        for barcode in ("789000000097", "789000000098"):
            response = self.client.post(
                reverse("product_create_from_modal"),
                {"nome": "Produto com variações", "descricao": "Descrição do produto com variações", "codigo_barras": barcode},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Produto.objects.filter(nome="Produto com variações").count(),
            2,
        )

    def test_update_product_records_user_who_updated_it(self):
        controle_data = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        product = Produto.objects.create(
            nome="Nome inicial",
            descricao="Descrição inicial",
            codigo_barras="789000000002",
            responsavel_cadastro=self.user,
            controle_data=controle_data,
        )
        product_link = Link.objects.create(
            nome="Link inicial",
            url="https://example.com/inicial",
            fornecedor=self.supplier,
            controle_data=controle_data,
        )
        product_value = ValorProduto.objects.create(
            produto=product,
            link=product_link,
            valor="100.00",
            controle_data=controle_data,
        )

        form_page_response = self.client.get(
            reverse("product_update", args=(product.pk,))
        )
        self.assertContains(form_page_response, "Link inicial")
        self.assertContains(form_page_response, "100.00")
        self.assertContains(form_page_response, self.supplier.nome_fornecedor)

        response = self.client.post(
            reverse("product_update", args=(product.pk,)),
            {
                "nome": "Nome atualizado",
                "descricao": "Descrição atualizada",
                "codigo_barras": product.codigo_barras,
                "link-nome": "Link atualizado",
                "link-url": "https://example.com/atualizado",
                "link-fornecedor": self.supplier.pk,
                "value-valor": "150.50",
            },
        )

        self.assertRedirects(response, reverse("product_list"))
        product.refresh_from_db()
        product.controle_data.refresh_from_db()
        product_link.refresh_from_db()
        product_value.refresh_from_db()
        self.assertEqual(product.nome, "Nome atualizado")
        self.assertEqual(product_link.nome, "Link atualizado")
        self.assertEqual(product_link.url, "https://example.com/atualizado")
        self.assertEqual(str(product_value.valor), "150.50")
        self.assertEqual(product.controle_data.usuario_atualizacao, self.user)

    def test_product_list_displays_new_fields(self):
        controle_data = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        Produto.objects.create(
            nome="Produto listado",
            descricao="Descrição do produto listado",
            codigo_barras="789000000003",
            responsavel_cadastro=self.user,
            controle_data=controle_data,
        )

        response = self.client.get(reverse("product_list"))

        self.assertContains(response, "Produto listado")
        self.assertContains(response, "789000000003")
        self.assertContains(response, "gestor")


class InventoryManagementTests(TestCase):
    def setUp(self):
        self.inventory_manager = get_user_model().objects.create_superuser(
            username="gestor_inventario",
            email="inventario@example.com",
            password="senha-segura",
        )
        self.client.force_login(self.inventory_manager)

    def test_inventory_list_opens_for_authorized_user(self):
        response = self.client.get(reverse("inventory_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inventário de Patrimônio")
        self.assertContains(response, reverse("inventory_create"))

    def test_create_inventory_item(self):
        response = self.client.post(
            reverse("inventory_create"),
            {
                "numero_patrimonio": "PAT-001",
                "id_ativo": "ATIVO-001",
                "categoria": "NOTE",
                "item_modelo": "Notebook de desenvolvimento",
                "serie_licenca": "SERIE-001",
                "data_aquisicao": "2026-08-12",
                "valor": "4500.00",
                "validade_garantia": "2027-08-12",
                "status": "ATIVO",
                "setor": "Tecnologia",
                "usuario": "",
                "observacoes": "Equipamento para desenvolvimento.",
            },
        )

        self.assertRedirects(response, reverse("inventory_list"))
        self.assertTrue(
            Inventario.objects.filter(numero_patrimonio="PAT-001").exists()
        )


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
            descricao="Notebook de desenvolvimento",
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
            valor_produto="3499.90",
            total="6999.80",
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
                "responsavel_fornecedor": "Maria",
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
        product_value = ValorProduto.objects.get(produto=self.produto, link=link)

        order_form_response = self.client.get(reverse("produto_pedido_create"))
        self.assertContains(order_form_response, "Cadastrar pedido de produto")
        self.assertContains(order_form_response, "Página do notebook")
        self.assertContains(order_form_response, "3499.90")
        self.assertContains(order_form_response, "Fornecedor do link selecionado")
        self.assertNotContains(order_form_response, 'name="status"')

        response = self.client.post(
            reverse("produto_pedido_create"),
            {
                "nome": "Notebook para desenvolvimento",
                "descricao": "Equipamento da equipe técnica",
                "produto": self.produto.pk,
                "link": link.pk,
                "quantidade_produto": 2,
                "valor_produto": "3499.90",
                "total": "6999.80",
            },
        )
        self.assertRedirects(response, reverse("produto_pedido_list"))
        produto_pedido = ProdutoPedido.objects.get(produto=self.produto)
        self.assertEqual(produto_pedido.status, "PENDENTE")
        self.assertEqual(produto_pedido.link, link)
        self.assertFalse(hasattr(produto_pedido, "valor_produto"))
        saved_product_value = produto_pedido.get_registered_product_value()
        self.assertEqual(saved_product_value, product_value)

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

    def test_create_supplier_from_product_modal(self):
        form_page_response = self.client.get(reverse("product_create"))

        self.assertEqual(form_page_response.status_code, 200)
        self.assertContains(form_page_response, "Adicionar fornecedor")
        self.assertContains(
            form_page_response,
            reverse("supplier_create_from_product"),
        )

        response = self.client.post(
            reverse("supplier_create_from_product"),
            {
                "nome_fornecedor": "Fornecedor cadastrado no modal",
                "cnpj_cnpj": "00.000.000/0004-00",
                "telefone_fornecedor": "(82) 99999-0004",
                "responsavel_fornecedor": "Carlos",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        created_supplier = Fornecedor.objects.get(
            id=response_data["supplier"]["id"]
        )
        self.assertEqual(
            created_supplier.nome_fornecedor,
            "Fornecedor cadastrado no modal",
        )
        self.assertEqual(
            created_supplier.controle_data.usuario_cadastro,
            self.user,
        )

    def test_update_records_user_in_control_data(self):
        controle = ControleData.objects.create(
            usuario_cadastro=self.user,
            usuario_atualizacao=self.user,
        )
        fornecedor = Fornecedor.objects.create(
            nome_fornecedor="Nome inicial",
            cnpj_cnpj="00.000.000/0002-00",
            telefone_fornecedor="(82) 3333-0000",
            responsavel_fornecedor="João",
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
                "responsavel_fornecedor": fornecedor.responsavel_fornecedor,
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
            responsavel_fornecedor="Ana",
            controle_data=controle,
        )

        response = self.client.post(reverse("fornecedor_delete", args=(fornecedor.pk,)))

        self.assertRedirects(response, reverse("fornecedor_list"))
        self.assertFalse(Fornecedor.objects.filter(pk=fornecedor.pk).exists())

