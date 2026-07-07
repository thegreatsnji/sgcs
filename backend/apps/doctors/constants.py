"""Constantes do módulo médico."""

CACHE_TTL = 120
CACHE_KEY_HISTORICO = "sgcs:doctors:historico:{paciente_id}"


class PrescricaoEstado:
    RASCUNHO = "RASCUNHO"
    ACTIVA = "ACTIVA"
    APROVADA = "APROVADA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"

    CHOICES = [
        (RASCUNHO, "Rascunho"),
        (ACTIVA, "Activa"),
        (APROVADA, "Aprovada"),
        (CONCLUIDA, "Concluída"),
        (CANCELADA, "Cancelada"),
    ]


class MedicamentoEstado:
    ACTIVO = "ACTIVO"
    SUSPENSO = "SUSPENSO"
    CONCLUIDO = "CONCLUIDO"

    CHOICES = [
        (ACTIVO, "Activo"),
        (SUSPENSO, "Suspenso"),
        (CONCLUIDO, "Concluído"),
    ]


class TratamentoEstado:
    EM_CURSO = "EM_CURSO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

    CHOICES = [
        (EM_CURSO, "Em curso"),
        (CONCLUIDO, "Concluído"),
        (CANCELADO, "Cancelado"),
    ]


class EvolucaoTipo:
    MELHORIA = "MELHORIA"
    AGRAVAMENTO = "AGRAVAMENTO"
    ESTAVEL = "ESTAVEL"
    OBSERVACAO = "OBSERVACAO"

    CHOICES = [
        (MELHORIA, "Melhoria"),
        (AGRAVAMENTO, "Agravamento"),
        (ESTAVEL, "Estável"),
        (OBSERVACAO, "Observação"),
    ]
