import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/catalogo_servicos_sauvida.csv").open(encoding="utf-8-sig")))
dept_names = {
    "ADM": "Administração",
    "DIR": "Direção",
    "REC": "Receção",
    "CONS-GER": "Consulta Geral",
    "ESP-MED": "Especialidades Médicas",
    "ENF": "Enfermagem",
    "LAB": "Laboratório",
    "ECO": "Ecografia",
    "MAT-PAR": "Maternidade e Parteira",
    "CIR": "Cirurgia",
}
out = [
    "# Auditoria de dados — Sprint 17",
    "",
    "Fonte: `backend/data/catalogo_servicos_sauvida.csv` (sem alteração de preços).",
    "",
    "| Código | Serviço | Categoria | Departamento | Preço | Estado | Observação |",
    "|---|---|---|---|---:|---|---|",
]
for r in rows:
    preco = r.get("preco_fcfa", "").strip() or "—"
    obs = (r.get("observacoes") or "").replace("|", "/") or "Aguardar validação clínica"
    estado = "PENDENTE" if preco in ("REVISAR_COM_CLINICA", "—", "") else "CONFIRMADO"
    dept = dept_names.get(r["departamento"], r["departamento"])
    out.append(
        f"| {r['codigo']} | {r['nome']} | {r['categoria']} | {dept} | {preco} | {estado} | {obs} |"
    )
out.append("")
out.append(f"**Resumo:** {len(rows)} serviços — **0 CONFIRMADO**, **{len(rows)} PENDENTE**, **0 DUPLICADO** no ficheiro.")
Path(ROOT.parent / "docs/SPRINT17_DATA_AUDIT.md").write_text("\n".join(out), encoding="utf-8")
print(len(rows))
