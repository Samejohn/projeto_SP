from django.db import models

class Inventario(models.Model):
    STATUS_CHOICES = [
        ("ATIVO", "Ativo"),
        ("MANUT", "Em Manutenção"),
        ("DESC", "Descartado"),
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
    id_ativo = models.CharField("ID do Inventario", max_length=30, unique=True)
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIA_CHOICES)
    item_modelo = models.CharField("Item / Modelo", max_length=150)
    serie_licenca = models.CharField("S/N (Série) / Licença", max_length=150, blank=True, null=True)
    data_aquisicao = models.DateField("Data Aquisição")
    valor = models.DecimalField("Valor (R$)", max_digits=12, decimal_places=2)
    validade_garantia = models.DateField("Validade / Garantia", blank=True, null=True)
    status = models.CharField("Status", max_length=15, choices=STATUS_CHOICES, default="ATIVO")
    setor = models.CharField("Setor", max_length=100)
    
    # Se Usuário
    usuario = models.OneToOneField('auth.User', verbose_name='Usuário', blank=True, null=True, on_delete=models.PROTECT)

    observacoes = models.TextField("Observações", blank=True, null=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "inventarios"
        ordering = ["numero_patrimonio"]

    def __str__(self):
        return f"{self.numero_patrimonio} - {self.item_modelo}"
