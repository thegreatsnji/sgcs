from django.db import models


class TipoMovimentoStockUrgencia(models.TextChoices):
    ENTRADA = "ENTRADA", "Entrada"
    SAIDA = "SAIDA", "Saída"
    AJUSTE = "AJUSTE", "Ajuste de inventário"
