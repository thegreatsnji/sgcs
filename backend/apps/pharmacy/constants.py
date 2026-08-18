from django.db import models


class CategoriaItemUrgencia(models.TextChoices):
    MEDICAMENTO = "MEDICAMENTO", "Medicamento"
    MATERIAL_CLINICO = "MATERIAL_CLINICO", "Material clínico"
    TESTE_RAPIDO = "TESTE_RAPIDO", "Teste rápido"
    OUTRO = "OUTRO", "Outro"


class TipoMovimentoStockUrgencia(models.TextChoices):
    ENTRADA = "ENTRADA", "Entrada"
    SAIDA = "SAIDA", "Saída"
    AJUSTE = "AJUSTE", "Ajuste de inventário"
    PERDA_EXPIRACAO = "PERDA_EXPIRACAO", "Perda / expiração"


class OrigemMovimentoStock(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    STOCK_INICIAL = "STOCK_INICIAL", "Stock inicial"
    STOCK_INICIAL_CLINICA = "STOCK_INICIAL_CLINICA", "Stock inicial da clínica"
    IMPORTACAO = "IMPORTACAO", "Importação"


class EstadoStockUrgencia(models.TextChoices):
    DISPONIVEL = "DISPONIVEL", "Disponível"
    STOCK_BAIXO = "STOCK_BAIXO", "Stock baixo"
    SEM_STOCK = "SEM_STOCK", "Sem stock"
    EXPIRADO = "EXPIRADO", "Expirado"
    PROXIMO_DA_VALIDADE = "PROXIMO_DA_VALIDADE", "Próximo da validade"
