# Catálogo laboratorial SauVida

## Fonte de preço

`TipoExameLaboratorio.servico` → `billing.Servico`. Não duplicar preço no tipo de exame.

## Ficheiro

`backend/data/exames_laboratoriais_sauvida.csv` — 9 exames iniciais (Hemograma, Glicemia, Ureia, Creatinina, Urina, Fezes, β-HCG, VIH, HBsAg).

Categorias laboratoriais no CSV: Bioquímica, Hematologia, Microbiologia, Parasitologia, Endocrinologia, Imunologia.

## Migração

Campos novos: `tipo_amostra`, `recipiente`, `instrucoes_colheita`, `exige_jejum`, `ordem`, `servico`.

## Laboratório operacional

`ExameLaboratorial` em pedidos continua por nome; alinhamento ao catálogo via tipos em settings + serviços `LAB-*`.
