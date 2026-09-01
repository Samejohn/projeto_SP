from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class EstoqueManager(models.Manager):
  
    def com_alerta_minimo(self):
        return self.filter(quantidade_estoque__lte=models.F('estoque_minimo'))
    
    def buscar_por_nome(self, termo):
        return self.filter(nome__icontains=termo)
    
    def com_movimentacoes_recentes(self, limite=10):
        return self.prefetch_related(
            models.Prefetch(
                'movimentacoes',
                queryset=MovimentacaoEstoque.objects.select_related('responsavel')
                .order_by('-data_movimentacao')[:limite]
            )
        )


class Estoque(models.Model):    
    nome = models.CharField('Produto', max_length=100, db_index=True)
    descricao = models.TextField('Descrição', blank=True, null=True)
    quantidade_estoque = models.PositiveIntegerField('Quantidade Disponível', default=0)
    estoque_minimo = models.PositiveIntegerField('Estoque Mínimo', default=5)
    codigo_barras = models.CharField('Código de Barras', max_length=50, unique=True, null=True, blank=True)
    valor_unitario_atual = models.DecimalField(
    'Valor Unitário Atual',
    max_digits=10,
    decimal_places=2,
    null=False,
    blank=False
    )
    
    responsavel_cadastro = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='estoque_cadastrados',
        verbose_name='Responsável pelo cadastro',
    )
    data_criacao = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    objects = EstoqueManager()

    class Meta:
        verbose_name = 'Produto em estoque'
        verbose_name_plural = 'Produtos em estoque'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['quantidade_estoque', 'estoque_minimo']),
        ]

    def __str__(self):
        return f'{self.nome} - {self.quantidade_estoque} un.'

    @property
    def alerta_estoque_minimo(self):
        """Retorna True se o estoque atual for menor ou igual ao estoque mínimo."""
        return self.quantidade_estoque <= self.estoque_minimo

    @property
    def valor_total_estoque(self):
        """Retorna o valor total do estoque."""
        return self.quantidade_estoque * self.valor_unitario_atual

    def atualizar_quantidade(self, quantidade, tipo_movimentacao, responsavel, valor_unitario=None):
        """Método seguro para atualizar quantidade com validação."""
        if tipo_movimentacao == MovimentacaoEstoque.TIPO_SAIDA:
            if self.quantidade_estoque < quantidade:
                raise ValidationError(
                    f'Estoque insuficiente. Disponível: {self.quantidade_estoque}, Solicitado: {quantidade}'
                )
            nova_quantidade = self.quantidade_estoque - quantidade
        else:  # Entrada
            nova_quantidade = self.quantidade_estoque + quantidade
        
        # Atualiza valor unitário se fornecido
        if valor_unitario is not None:
            self.valor_unitario_atual = valor_unitario
        
        self.quantidade_estoque = nova_quantidade
        self.save()
        
        # Registra movimentação
        return MovimentacaoEstoque.objects.create(
            estoque=self,
            tipo=tipo_movimentacao,
            quantidade=quantidade,
            valor_unitario=valor_unitario or self.valor_unitario_atual,
            responsavel=responsavel
        )


class MovimentacaoEstoque(models.Model):
    
    TIPO_ENTRADA = 'E'
    TIPO_SAIDA = 'S'
    TIPO_CHOICES = [
        (TIPO_ENTRADA, 'Entrada'),
        (TIPO_SAIDA, 'Saída'),
    ]

    estoque = models.ForeignKey(
        Estoque, 
        on_delete=models.CASCADE, 
        related_name='movimentacoes',
        verbose_name='Item do Estoque'
    )
    tipo = models.CharField('Tipo de Movimentação', max_length=1, choices=TIPO_CHOICES, db_index=True)
    quantidade = models.PositiveIntegerField('Quantidade')
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, editable=False)
    
    data_movimentacao = models.DateTimeField('Data da Movimentação', auto_now_add=True, db_index=True)
    observacao = models.TextField('Observação', blank=True, null=True)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Responsável'
    )

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data_movimentacao']
        indexes = [
            models.Index(fields=['estoque', '-data_movimentacao']),
            models.Index(fields=['tipo', 'data_movimentacao']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.estoque.nome} - {self.quantidade} un.'

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantidade) * Decimal(self.valor_unitario)
        super().save(*args, **kwargs)


class EstoqueMovimentoBatch(models.Model):    
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200)
    finalizado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Movimento em Lote'
        verbose_name_plural = 'Movimentos em Lote'