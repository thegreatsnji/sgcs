# Pacote piloto SauVida V1

## Objectivo

Validar receção, faturação, reduções, pagamentos parciais, recibos e catálogo **SAUVIDA_V1** durante **3–5 dias úteis**.

## Módulos no piloto

- Receção / faturação / recibos / catálogo V1 / laboratório (consulta de pedidos, se activo)

## Fora do piloto

- Migração Access completa, relatórios avançados não validados, alterações de catálogo sem versão nova

## Checklist pré-arranque

- [ ] Backup `backup_pre_catalogo_sauvida_v1`
- [ ] Dry-run import V1 aprovado
- [ ] Apply import + `archive_legacy_catalog`
- [ ] Alinhamento lab dry-run/apply aprovado
- [ ] UAT receção e recibo iniciados

## Durante o piloto

- Backup diário; não apagar dados; registar problemas por perfil; distinguir bug vs formação

## Contingência

Em falha crítica: modo manual (recibos papel) + restaurar backup se necessário; contacto técnico interno.

## Critérios de aprovação

UAT receção ≥ 90% casos APROVADO; zero import de pendentes; catálogo legado invisível na receção.
