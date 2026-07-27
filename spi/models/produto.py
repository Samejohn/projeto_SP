from django.db import models

class Produto(models.Model):
    nome_produto = models.CharField(max_length=255)
    link_produto = models.URLField(max_length=2048)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_produto = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome_produto

   