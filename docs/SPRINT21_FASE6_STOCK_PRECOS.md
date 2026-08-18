# Sprint 21 Fase 6 — Stock de urgência e preçários

**Estado:** `AGUARDA_VALIDACAO_STOCK_E_PRECOS`  
**Sem importação para a BD. Sem alteração do catálogo SAUVIDA_V1.**

## Fontes

- Catálogo V1 (`backend/data/releases/catalogo_sauvida_v1.csv`)
- Candidatos históricos de stock (Excel/CSV privados da migração)
- Transcrição das fotografias operacionais actuais (Medicamentos disponíveis p.1–2 e preçário clínico)

As fotografias originais devem ficar em `backend/data/private/sauvida_atual/fotos/` (gitignored).

## Regras

- Grafias tipo CETRIAXONA / CEFRIAZOMA / CETROXONA / CITROXONA **não** são fundidas.
- `CX/50`, `2CX/10`, `1T`, `4L/7CP` e números isolados **não** são convertidos em unidades.
- Preços das fotos são **preço de referência**, não custo nem margem.
- Cartões (vacina / grávida) não entram no stock de medicamentos sem decisão clínica.
- `SAUVIDA_V1_1` só após confirmação da Direcção.

## Saídas privadas

Geradas por `python manage.py generate_sauvida_current_pack` em `backend/data/private/sauvida_atual/`.
