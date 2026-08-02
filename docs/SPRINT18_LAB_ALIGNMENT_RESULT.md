# Sprint 18 — Alinhamento laboratório (resultado)

## Pré-requisitos

- Serviços `LAB-*` materializados na base de dados.
- Tipos de exame importados (`exames_laboratoriais_sauvida.csv`).

## Comandos

```bash
python manage.py align_lab_services --dry-run   # log: docs/logs/sprint18_lab_alignment_dry_run.txt
python manage.py align_lab_services --apply     # log: docs/logs/sprint18_lab_alignment_apply.txt
```

## Mapa previsto (9 exames)

| Exame | Código tipo | Serviço | Estado | Preço | Resultado |
|---|---|---|---|---:|---|
| Hemograma Completo | LAB-HEMO-TIPO | LAB-HEMO | Pendente BD | Catálogo | Aguardar materialização + apply |
| Glicemia | LAB-GLIC-TIPO | LAB-GLIC | Pendente BD | Catálogo | Idem |
| Ureia | LAB-UREIA-TIPO | LAB-UREIA | Pendente BD | Catálogo | Idem |
| Creatinina | LAB-CREAT-TIPO | LAB-CREAT | Pendente BD | Catálogo | Idem |
| Exame de Urina | LAB-URINA-TIPO | LAB-URINA | Pendente BD | Catálogo | Idem |
| Exame de Fezes | LAB-FEZES-TIPO | LAB-FEZES | Pendente BD | Catálogo | Idem |
| β-HCG | LAB-HCG-TIPO | LAB-HCG | Pendente BD | Catálogo | Idem |
| Teste VIH | LAB-VIH-TIPO | LAB-VIH | Pendente BD | Catálogo | Idem |
| HBsAg | LAB-HBS-TIPO | LAB-HBS | Pendente BD | Catálogo | Idem |

**Fonte de preço:** sempre `Servico.preco` após confirmação clínica (`preco_confirmado=true`).

## Regras respeitadas

- Sem correspondência por nome aproximado.
- Sem associação se serviço ausente ou inactivo sem autorização.
