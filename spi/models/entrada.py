from django.db import models
from django.contrib.auth.models import User

class Entrada(models.Model):
    # Produto do catálogo recebido nesta entrada.
    produto = models.ForeignKey(
        'spi.Produto', 
        on_delete=models.CASCADE, 
        related_name='entradas',
        verbose_name="Produto"
    )
    
    # Quantidades e Valores
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Recebida")
    preco_custo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço de Custo (Unidade)"
    )
    
    # Documentação e Origem
    nota_fiscal = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Nº NF" # NF: Nota Fiscal
    )
    ordem_fornecimento = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Nº OF" # OF: Ordem de Fornecimento
    )
    fornecedor = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Fornecedor"
    )
    
    # Controle e Auditoria
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Responsável"
    )
    data_entrada = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data/Hora"
    )
    observacao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observação"
    )

    def save(self, *args, **kwargs):
        from spi.stock_automation import save_record_and_synchronize_stock

        save_record_and_synchronize_stock(self, super().save, *args, **kwargs)

    class Meta:
        ordering = ['-data_entrada']
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    def __str__(self):
        return f"Entrada #{self.id} - {self.produto} ({self.quantidade} un)"

    @property
    def total(self):
        """Calcula o valor total da entrada (Quantidade x Preço de Custo)"""
        if self.quantidade and self.preco_custo:
            return self.quantidade * self.preco_custo
        return 0.00
