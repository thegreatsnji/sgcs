# Priorização da revisão histórica

**Data:** 2026-08-17  
Apenas agregados. Sem nomes, telefones ou outros identificadores.

Os 739 avisos da Fase 1 **não** são todos bloqueantes. A reclassificação gerou 765 linhas priorizadas (inclui 23 pares de duplicados e 3 médicos).

## Totais

| Métrica | Valor |
| --- | --- |
| Total priorizado | 765 |
| **Bloqueante** | **141** |
| Não bloqueante | 624 |
| Pacientes bloqueados (duplicado sem decisão) | 38 |
| Pares de duplicados | 23 |
| Laboratório bloqueado (`AMBIGUO`) | 13 |
| Datas bloqueadas | 5 (4 ligadas a eventos históricos) |
| Stock bloqueado (nome canónico incerto) | 98 |
| Eventos sem paciente (arquivo, não importar) | 173 |

## O que é bloqueante

- possível duplicado de paciente (não mesclar);
- data suspeita / impossível;
- mapeamento laboratorial `AMBIGUO`;
- conflito preço/desconto/líquido;
- nome de medicamento incerto **se** se for criar item de stock.

## O que não bloqueia a importação

- telefone, residência, nascimento ou sexo ausentes;
- médico histórico sem utilizador SGCS (`medico_sgcs` fica vazio);
- exame `POSSIVEL` ou `SEM_CORRESPONDENCIA` (histórico textual);
- descrição antiga de consulta/ecografia/cirurgia;
- linhas sem paciente (ficam no arquivo privado).

## Ficheiros privados (fora do Git)

- `migracao_revisao_priorizada.csv`
- `duplicados_para_validacao_clinica.csv` (`MESMA_PESSOA` / `PESSOAS_DIFERENTES` / `INDETERMINADO`)
- `datas_validacao_clinica.csv`
- `eventos_sem_paciente.csv`
- `stock_validacao_enfermagem.csv`

`INDETERMINADO` = dois registos separados. Nunca fundir só pelo nome.
