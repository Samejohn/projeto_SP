from django.db import models


class Inventario(models.Model):
    STATUS_CHOICES = [
        ("ATIVO", "Ativo"),
        ("MANUT", "Em Manutenção"),
        ("DESC", "Descartado"),
    ]

    ID_CHOICES = [
        ("HW", "Hardware"),
        ("SW", "Software"),
        ("SRV", "Servidor"),
        ("NET", "Rede"),
        ("PER", "Periféricos"),
        ("CLD", "Serviços em nuvem"),
        ("SEC", "Segurança"),
        ("LIC", "Licenças"),
    ]

    CATEGORIA_CHOICES = [
        ("NOTE", "Notebook"),
        ("DESK", "Desktop"),
        ("MONI", "Monitor"),
        ("IMP", "Impressora"),
        ("NOBR", "Nobreak"),
        ("SERV", "Servidor"),
        ("OUTR", "Outros"),
    ]

    numero_patrimonio = models.CharField("Nº Patrimônio", max_length=30, unique=True)
    # Removido unique=True para permitir repetir a categoria entre itens distintos
    id_ativo = models.CharField("ID do Inventario", max_length=30, choices=ID_CHOICES)
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIA_CHOICES)
    item_modelo = models.CharField("Item / Modelo", max_length=150)
    serie_licenca = models.CharField("S/N (Série) / Licença", max_length=150, blank=True, null=True)
    data_aquisicao = models.DateField("Data Aquisição")
    quantidade = models.PositiveIntegerField("Quantidade", default=1)
    valor = models.DecimalField("Valor (R$)", max_digits=12, decimal_places=2)
    total = models.DecimalField("Total (R$)", max_digits=12, decimal_places=2, blank=True, null=True)
    validade_garantia = models.DateField("Validade / Garantia", blank=True, null=True)
    status = models.CharField("Status", max_length=15, choices=STATUS_CHOICES, default="ATIVO")
    setor = models.CharField("Setor", max_length=100)
    
    # Alterado para ForeignKey para permitir que um usuário possua vários equipamentos
    usuario = models.ForeignKey(
        'auth.User',
        verbose_name='Usuário',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inventarios"
    )

    observacoes = models.TextField("Observações", blank=True, null=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def save(self, *args, **kwargs):
        if self.quantidade is not None and self.valor is not None:
            self.total = self.quantidade * self.valor
        else:
            self.total = 0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Inventário"
        verbose_name_plural = "Inventários"
        ordering = ["numero_patrimonio"]

    def __str__(self):
        return f"{self.numero_patrimonio} - {self.item_modelo}"

