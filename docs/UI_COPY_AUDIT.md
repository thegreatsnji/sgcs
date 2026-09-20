# Auditoria de copy da interface

Revisão de textos visíveis no SGCS (Clínica SauVida). Código, URLs, classes CSS e termos com hífen linguístico (ex.: Guiné-Bissau, e-mail) não foram alterados.

## Áreas revistas

- Cabeçalho, rodapé, login e layout de autenticação
- Painéis por perfil (administração, direcção, médico, enfermagem, receção, laboratório, financeiro)
- Receção, faturação, consultas, pacientes, stock de urgência, relatórios e notificações
- Página 404 e ErrorBoundary

## Padrões removidos

- Travessão (`—`) como separador em títulos, subtítulos e frases (`Stock baixo — 5` passou a dois pontos ou frase completa)
- Slogans promocionais no ecrã de acesso
- “Bem-vindo” genérico no painel administrativo

## Terminologia padronizada

- Clínica SauVida
- Sistema de Gestão Clínica SauVida
- Stock de Urgência
- Receção
- Laboratório
- Consultas
- Pacientes / utentes (mantido o uso já aprovado: “utente” na receção, “paciente” na área clínica)

## Excepções

- Comentários de código e documentação interna
- Intervalos numéricos de laboratório (`valor_minimo – valor_maximo`)
- Hífen em palavras compostas e em valores negativos
