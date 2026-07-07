"""Constantes do módulo de notificações."""

CACHE_KEY_NAO_LIDAS = "notifications:nao_lidas:{user_id}"
CACHE_KEY_CONTADOR = "notifications:contador:{user_id}"
CACHE_KEY_DASHBOARD = "notifications:dashboard"
CACHE_TTL = 120


class NotificacaoEstado:
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    ENVIADA = "ENVIADA"
    ENTREGUE = "ENTREGUE"
    LIDA = "LIDA"
    FALHOU = "FALHOU"
    CANCELADA = "CANCELADA"

    CHOICES = [
        (PENDENTE, "Pendente"),
        (PROCESSANDO, "A processar"),
        (ENVIADA, "Enviada"),
        (ENTREGUE, "Entregue"),
        (LIDA, "Lida"),
        (FALHOU, "Falhou"),
        (CANCELADA, "Cancelada"),
    ]


class NotificacaoTipo:
    INFORMATIVA = "INFORMATIVA"
    SUCESSO = "SUCESSO"
    AVISO = "AVISO"
    ERRO = "ERRO"
    LEMBRETE = "LEMBRETE"
    URGENTE = "URGENTE"

    CHOICES = [
        (INFORMATIVA, "Informativa"),
        (SUCESSO, "Sucesso"),
        (AVISO, "Aviso"),
        (ERRO, "Erro"),
        (LEMBRETE, "Lembrete"),
        (URGENTE, "Urgente"),
    ]


class NotificacaoCanal:
    INTERNO = "INTERNO"
    EMAIL = "EMAIL"
    SMS = "SMS"

    CHOICES = [
        (INTERNO, "Interno"),
        (EMAIL, "E-mail"),
        (SMS, "SMS"),
    ]
