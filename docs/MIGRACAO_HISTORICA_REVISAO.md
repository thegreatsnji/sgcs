# Revisão da migração histórica

A Fase 2 **não** pede à clínica que complete os 181 utentes sem telefone/nascimento antes de importar.

## Bloqueante (antes do apply completo)

1. **23 pares** em `duplicados_para_validacao_clinica.csv` — `MESMA_PESSOA`, `PESSOAS_DIFERENTES` ou `INDETERMINADO`.
2. **5 datas** em `datas_validacao_clinica.csv`.
3. **13 eventos laboratoriais AMBIGUO** — não ligar ao catálogo V1.
4. Stock: a enfermeira preenche `stock_validacao_enfermagem.csv` **antes** de criar stock actual (`quantidade_inicial` continua vazia).

## Não bloqueante

- 181 candidatos incompletos → importar como `IMPORTADO_NAO_VERIFICADO`.
- 3 médicos sem utilizador → `medico_original` na origem, `medico_sgcs` vazio.
- Exames sem correspondência moderna → histórico textual.
- 173 eventos sem paciente → arquivo, sem utente fictício.

## Confirmação na receção

A ficha de um utente importado mostra um aviso discreto. «Confirmar dados» marca `VERIFICADO` e **não** bloqueia o atendimento.
