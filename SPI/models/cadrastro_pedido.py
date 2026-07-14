# sua_app/models.py
from django.db import models
from django.contrib.auth.models import User

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Código/SKU")
    quantidade_atual = models.PositiveIntegerField(default=0, verbose_name="Estoque Atual")

    def __str__(self):
        return f"{self.nome} ({self.quantidade_atual} un)"

class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada de Estoque'),
        ('SAIDA', 'Saída/Venda'),
        ('DESCARTE', 'Descarte/Perda'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='DESCARTE')
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade a Descartar")
    motivo_descarte = models.TextField(verbose_name="Motivo do Descarte")
    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Operador Responsável")
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DESCARTE - {self.produto.nome} ({self.quantidade} un) por {self.operador}"