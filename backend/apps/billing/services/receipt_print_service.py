"""Dados de impressão do recibo SauVida."""

from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.billing.constants import MetodoPagamento, PagamentoEstado
from apps.billing.models import Pagamento, Recibo
from apps.settings.models import ConfiguracaoFaturacao
from apps.settings.services.settings_service import SettingsService


def _parse_numero_livro(numero: str) -> dict[str, str]:
    """REC-2026-000042 → sequência e ano como no livro de recibos."""
    parts = numero.split("-")
    if len(parts) >= 3 and parts[0] == "REC":
        try:
            sequencia = f"{int(parts[-1]):06d}"
        except ValueError:
            sequencia = parts[-1]
        return {"sequencia": sequencia, "ano": parts[1]}
    return {"sequencia": numero, "ano": str(timezone.now().year)}


def _data_emissao_parts(dt) -> dict[str, str]:
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return {"dia": f"{dt.day:02d}", "mes": f"{dt.month:02d}", "ano": str(dt.year)}


def _extenso_fcfa_simples(valor: Decimal) -> str:
    inteiro = int(valor)
    return f"{inteiro:,} francos CFA".replace(",", " ")


def build_receipt_print_context(recibo: Recibo) -> dict:
    pagamento = (
        Pagamento.objects.select_related("recebido_por", "fatura", "fatura__paciente")
        .get(pk=recibo.pagamento_id)
    )
    fatura = pagamento.fatura
    paciente = fatura.paciente
    config = SettingsService._get_singleton(ConfiguracaoFaturacao)
    perfil = SettingsService.get_clinic_profile()

    total_cobrado = fatura.total
    total_pago = sum(
        p.valor for p in fatura.pagamentos.filter(estado=PagamentoEstado.CONFIRMADO)
    )
    saldo = max(total_cobrado - total_pago, Decimal("0.00"))

    itens = []
    total_oficial = Decimal("0.00")
    total_reducao = Decimal("0.00")
    for item in fatura.itens.select_related("servico"):
        oficial = getattr(item, "preco_oficial", item.preco) or item.preco
        linha_oficial = oficial * item.quantidade
        total_oficial += linha_oficial
        reducao = getattr(item, "valor_reducao", Decimal("0.00")) or Decimal("0.00")
        total_reducao += reducao
        itens.append(
            {
                "nome": item.servico.nome,
                "quantidade": item.quantidade,
                "preco_oficial": str(oficial),
                "preco_cobrado": str(item.preco),
                "subtotal_cobrado": str(item.subtotal),
                "valor_reducao": str(reducao),
            }
        )

    referente = ", ".join(i["nome"] for i in itens[:5])
    if len(itens) > 5:
        referente += f" (+{len(itens) - 5})"

    exator_nome = ""
    if pagamento.recebido_por:
        exator_nome = pagamento.recebido_por.get_full_name() or pagamento.recebido_por.email

    metodo_label = dict(MetodoPagamento.choices).get(
        pagamento.metodo_pagamento, pagamento.metodo_pagamento
    )

    return {
        "recibo": {
            "numero": recibo.numero,
            "emitido_em": recibo.emitido_em.isoformat(),
            "segunda_via": recibo.segunda_via,
            "tipo_documento": "SEGUNDA VIA" if recibo.segunda_via else "ORIGINAL",
            "numero_livro": _parse_numero_livro(recibo.numero),
            "data_emissao": _data_emissao_parts(recibo.emitido_em),
        },
        "clinica": {
            "nome": perfil.get("nome") or "Clínica SauVida",
            "morada": perfil.get("morada") or "",
            "telefone": perfil.get("telefone") or perfil.get("telemovel") or "",
            "email": perfil.get("email") or "",
            "mensagem_rodape": perfil.get("mensagem_rodape") or config.texto_rodape_recibo,
            "mostrar_ministerio": config.mostrar_ministerio_saude_recibo,
            "republica": "República da Guiné-Bissau",
            "logotipo_url": perfil.get("logotipo"),
        },
        "exator": {"nome": exator_nome},
        "paciente": {
            "nome": paciente.full_name,
            "numero_processo": getattr(paciente, "patient_number", "") or str(paciente.pk),
        },
        "fatura": {"numero": fatura.numero, "total_cobrado": str(total_cobrado)},
        "pagamento": {
            "valor": str(pagamento.valor),
            "metodo": pagamento.metodo_pagamento,
            "metodo_label": metodo_label,
            "valor_extenso": _extenso_fcfa_simples(pagamento.valor)
            if config.mostrar_valor_por_extenso
            else "",
        },
        "totais": {
            "preco_oficial_total": str(total_oficial),
            "reducao_total": str(total_reducao),
            "total_cobrado": str(total_cobrado),
            "total_pago": str(total_pago),
            "saldo": str(saldo),
        },
        "itens": itens,
        "referente_a": referente,
        "config": {
            "mostrar_preco_oficial": config.mostrar_preco_oficial_recibo,
            "mostrar_reducao": config.mostrar_reducao_recibo or config.mostrar_reducao_no_recibo,
            "mostrar_saldo": config.mostrar_saldo_recibo,
            "formato": config.formato_recibo,
        },
        "textos": {
            "recebi_de": "Recebi do/a senhor/a",
            "importancia_de": "Importância de",
            "referente_a": "Referente a",
            "exator": "Exator (a)",
            "data": "Data",
        },
    }
