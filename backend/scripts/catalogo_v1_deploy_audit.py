"""Pré-verificação e auditoria pós-import Catálogo V1 (sem novo módulo Django)."""

from __future__ import annotations

import csv
import hashlib
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import django

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings  # noqa: E402
from django.db.models import Count  # noqa: E402

from apps.audit_logs.models import AuditAction, AuditLog  # noqa: E402
from apps.billing.constants import CATALOGO_VERSAO_ATIVA  # noqa: E402
from apps.billing.models import ItemFatura, Servico  # noqa: E402
from apps.settings.models import TipoExameLaboratorio  # noqa: E402

RELEASES = ROOT / "data" / "releases"
CATALOGO = RELEASES / "catalogo_sauvida_v1.csv"
EXAMES = RELEASES / "exames_laboratoriais_sauvida_v1.csv"
DOCS = ROOT.parent / "docs"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight() -> bool:
    db = settings.DATABASES["default"]
    print("=== PRÉ-VERIFICAÇÃO ===")
    print(f"ENGINE={db.get('ENGINE')}")
    print(f"NAME={db.get('NAME')}")
    print(f"HOST={db.get('HOST')}")
    print(f"catalogo_exists={CATALOGO.is_file()}")
    print(f"exames_exists={EXAMES.is_file()}")
    print(f"checksum_catalogo={sha256(CATALOGO)}")
    print(f"checksum_exames={sha256(EXAMES)}")

    rows = list(csv.DictReader(CATALOGO.open(encoding="utf-8-sig")))
    codes = [r["codigo"].strip() for r in rows]
    dup = [c for c, n in Counter(codes).items() if n > 1]
    pending = [
        r
        for r in rows
        if (r.get("estado") or "").upper() == "REVISAR_COM_CLINICA"
        or (r.get("preco_confirmado") or "").upper() == "FALSE"
    ]
    neg = []
    for r in rows:
        try:
            if Decimal(str(r.get("preco_fcfa") or "0")) < 0:
                neg.append(r["codigo"])
        except Exception:
            neg.append(r["codigo"])

    ok = (
        len(rows) == 119
        and not dup
        and not pending
        and not neg
        and all((r.get("versao_catalogo") or "").strip() == CATALOGO_VERSAO_ATIVA for r in rows)
    )
    print(f"linhas={len(rows)} dup={dup} pending={len(pending)} neg={neg} ok={ok}")
    return ok


def post_import_audit() -> str:
    v1 = Servico.objects.filter(versao_catalogo=CATALOGO_VERSAO_ATIVA)
    total = v1.count()
    activo = v1.filter(activo=True).count()
    confirmado = v1.filter(preco_confirmado=True).count()
    arquivado = v1.filter(arquivado=True).count()
    sem_preco = v1.filter(preco_confirmado=False).count()
    zero = v1.filter(preco=Decimal("0")).count()
    neg = v1.filter(preco__lt=0).count()
    dup_codes = (
        Servico.objects.values("codigo")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .count()
    )
    por_cat = dict(v1.values("categoria").annotate(c=Count("id")).values_list("categoria", "c"))
    audits = AuditLog.objects.filter(action=AuditAction.CATALOGO_REAL_IMPORTADO).count()
    items_before = ItemFatura.objects.count()

    lines = [
        "# Validação pós-importação — Catálogo V1",
        "",
        f"Ambiente: `{settings.DATABASES['default'].get('NAME')}` @ `{settings.DATABASES['default'].get('HOST')}`",
        "",
        "| Verificação | Esperado | Obtido | Estado |",
        "|---|---:|---:|---|",
        f"| Serviços SAUVIDA_V1 | 119 | {total} | {'APROVADO' if total == 119 else 'FALHOU'} |",
        f"| Activos | 119 | {activo} | {'APROVADO' if activo == 119 else 'NECESSITA REVISÃO'} |",
        f"| Preço confirmado | 119 | {confirmado} | {'APROVADO' if confirmado == 119 else 'FALHOU'} |",
        f"| Arquivados V1 | 0 | {arquivado} | {'APROVADO' if arquivado == 0 else 'FALHOU'} |",
        f"| Sem preço confirmado | 0 | {sem_preco} | {'APROVADO' if sem_preco == 0 else 'FALHOU'} |",
        f"| Preços negativos | 0 | {neg} | {'APROVADO' if neg == 0 else 'FALHOU'} |",
        f"| Códigos duplicados (global) | 0 | {dup_codes} | {'APROVADO' if dup_codes == 0 else 'FALHOU'} |",
        f"| Eventos CATALOGO_REAL_IMPORTADO | >0 | {audits} | {'APROVADO' if audits else 'NECESSITA REVISÃO'} |",
        f"| Itens fatura (preservação) | — | {items_before} linhas | APROVADO |",
        "",
        "## Por categoria",
        "",
    ]
    for cat, c in sorted(por_cat.items()):
        lines.append(f"- {cat}: {c}")
    lines.append("")
    lines.append(
        "Nota: alterações em `Servico` não recalculam `ItemFatura` nem recibos já emitidos (snapshots por linha)."
    )
    out = DOCS / "VALIDACAO_POS_IMPORTACAO_CATALOGO_V1.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {out}")
    return out.read_text(encoding="utf-8")


def lab_alignment_audit() -> None:
    import csv

    rows = list(csv.DictReader(EXAMES.open(encoding="utf-8-sig")))
    lines = [
        "# Validação alinhamento laboratorial V1",
        "",
        "| Exame | Código | Serviço correspondente | Estado | Problema |",
        "|---|---|---|---|---|",
    ]
    ok = pend = ambig = 0
    for row in rows:
        nome = row["nome"].strip()
        cod = row["codigo"].strip()
        sc = (row.get("servico_codigo") or "").strip()
        svc = Servico.objects.filter(codigo=sc).first() if sc else None
        tipo = TipoExameLaboratorio.objects.filter(codigo=cod).first()
        if not svc:
            st, prob = "SEM_SERVICO", "Serviço ausente na BD"
            pend += 1
        elif not tipo:
            st, prob = "SEM_TIPO", "Tipo exame não materializado"
            pend += 1
        elif tipo.servico_id and tipo.servico_id != svc.pk:
            st, prob = "AMBIGUO", f"Ligado a {tipo.servico.codigo}"
            ambig += 1
        elif tipo.servico_id == svc.pk:
            st, prob = "ALINHADO", ""
            ok += 1
        else:
            st, prob = "PENDENTE", "Sem ligação servico"
            pend += 1
        lines.append(f"| {nome} | {cod} | {sc or '-'} | {st} | {prob} |")
    lines.extend(
        [
            "",
            f"**Resumo:** alinhados={ok} | pendentes/sem serviço={pend} | ambíguos={ambig}",
            "",
            "Preço operacional: proveniente de `Servico.preco` (tipo não mantém preço concorrente).",
        ]
    )
    out = DOCS / "VALIDACAO_ALINHAMENTO_LAB_V1.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {out} (alinhados={ok}, ambig={ambig})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preflight"
    if cmd == "preflight":
        sys.exit(0 if preflight() else 1)
    if cmd == "post":
        post_import_audit()
        sys.exit(0)
    if cmd == "lab":
        lab_alignment_audit()
        sys.exit(0)
    print("Uso: preflight | post | lab")
    sys.exit(1)
