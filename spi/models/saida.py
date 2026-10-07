from django.db import models
from django.contrib.auth.models import User

class SaidaProduto(models.Model):
    MOTIVO_CHOICES = [
        ('USO_INTERNO', 'Uso Interno'),
        ('VENDA', 'Venda'),
        ('DESCARTE', 'Descarte / Avaria'),
        ('TRANSFERENCIA', 'Transferência'),
        ('OUTRO', 'Outro'),
    ]

    codigo_produto = models.CharField(max_length=50, verbose_name="Código do Produto")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    quantidade_saida = models.PositiveIntegerField(verbose_name="Quantidade Saída")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário (R$)")
    motivo_destino = models.CharField(max_length=50, choices=MOTIVO_CHOICES, verbose_name="Motivo / Destino")
    setor = models.CharField(max_length=100, verbose_name="Setor")
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Responsável")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    @property
    def total(self):
        return self.quantidade_saida * self.valor_unitario

    def __str__(self):
        return f"Saída #{self.id} - {self.descricao}"

    def save(self, *args, **kwargs):
        from spi.stock_automation import save_record_and_synchronize_stock

        save_record_and_synchronize_stock(self, super().save, *args, **kwargs)

    class Meta:
        verbose_name = "Saída de Produto"
        verbose_name_plural = "Saídas de Produtos"
        ordering = ['-data_hora']
        default_permissions = ('add', 'change', 'delete', 'view')