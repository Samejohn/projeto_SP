from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Estoque(models.Model):
    produto = models.CharField(
        max_length=150,
        verbose_name='Produto'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    quantidade = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade em estoque'
    )
    entrada = models.PositiveIntegerField(
        default=0,
        verbose_name='Entrada'
    )
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Unitário'
    )
    estoque_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque Mínimo'
    )
    responsavel = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Responsável'
    )
    localizacao = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Localização'
    )
    data = models.DateField(
        auto_now_add=True,
        verbose_name='Data'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['produto']
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return self.produto

    @property
    def total(self):
        if self.quantidade and self.valor_unitario:
            return self.quantidade * self.valor_unitario
        return Decimal('0.00')


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.CASCADE,
        related_name='movimentacoes'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.estoque.produto} ({self.quantidade})"

    def save(self, *args, **kwargs):
        """Atualiza automaticamente a quantidade do estoque."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if self.tipo == 'ENTRADA':
                self.estoque.quantidade = models.F('quantidade') + self.quantidade
                self.estoque.entrada = models.F('entrada') + self.quantidade
            elif self.tipo == 'SAIDA':
                self.estoque.quantidade = models.F('quantidade') - self.quantidade
            self.estoque.save(update_fields=['quantidade', 'entrada'])