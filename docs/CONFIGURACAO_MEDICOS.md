# Configuração dos médicos

## Modelo

`clinic_settings.MedicoPerfil` (1:1 com `User`, perfil `MEDICO`):

- especialidade, departamento
- numero_profissional
- dias_trabalho, horario_atendimento (JSON)
- duracao_consulta_minutos
- servico_consulta → `billing.Servico` (preço da consulta)
- activo, disponivel_marcacao

## Regra de preço

O valor cobrado na fatura vem do **Serviço** ligado (`servico_consulta`), não do utilizador.

## Próximo passo

Expor CRUD administrativo na UI de utilizadores (Sprint 17) — modelo e migration já criados.
