# UAT — Stock de urgência (enfermagem)

Ambiente: piloto / desenvolvimento. Perfil: **ENFERMEIRO**.

## Fluxo

1. Abrir `/stock`.
2. Pesquisar um item.
3. Ver quantidade actual (não editável na tabela).
4. **+ Entrada** +5 → confirmar novo stock.
5. **− Saída** −2 → confirmar novo stock.
6. Tentar saída maior que o disponível → deve bloquear.
7. Abrir **Histórico** → actor e data presentes.
8. **+ Novo item** (nome, categoria, unidade, quantidade inicial).
9. Definir stock mínimo.
10. Validar alerta **stock baixo**.
11. Validar estado **sem stock**.

## Regras

- Entrada: chegou material.
- Saída: foi usado.
- Ajuste: contagem física diferente.
- Perda/expiração: deixou de ser utilizável.
- Nunca editar a quantidade à mão.

Checklist a assinar na clínica após a ficha ter quantidades confirmadas.
