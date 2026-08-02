# Formação — Médico (≈ 25 min)

## Objectivo

Gerir fila, consulta clínica, pedidos de laboratório e histórico do paciente.

## Login

URL piloto → credenciais **Médico** → **Painel Médico**.

## Tarefas diárias

- Ver **pacientes hoje** e **próximo paciente**.
- **Fila de consultas** → iniciar / concluir consulta.
- Registar **sinais vitais**, **SOAP**, **diagnósticos**.
- **Pedir exames** (laboratório alinhado ao catálogo).
- Consultar **resultados** publicados.
- **Seguimentos** / nova marcação quando necessário.

## Atalhos / navegação

- Painel: `/dashboard/doctor`
- Fila: Consultas → fila
- Paciente: pesquisa global ou a partir da fila

## Erros comuns

- Consulta não iniciada — estado não muda para «em curso».
- Pedido lab. sem serviço correspondente — usar exames do catálogo V1.
- Sair sem concluir — fila fica incorrecta; sempre **concluir** ou documentar.

## Suporte

Hora + paciente (n.º processo) + passo onde falhou → coordenador clínico / TI.

## Sair da sessão

Logout explícito em posto partilhado.

## Segurança

- Acesso só a pacientes da sua actividade clínica (RBAC).
- Não partilhar login; não exportar PDFs para canais pessoais.
