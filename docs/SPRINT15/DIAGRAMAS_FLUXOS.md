# Diagramas — fluxos clínica vs. SGCS

Ver também [FLUXOS_REAIS_VALIDADOS.md](./FLUXOS_REAIS_VALIDADOS.md).

---

## 1. Jornada do paciente (núcleo actual)

```mermaid
sequenceDiagram
  participant P as Paciente
  participant R as Receção
  participant F as Fila
  participant M as Médico
  participant L as Laboratório
  participant B as Faturação

  P->>R: Chegada / identificação
  R->>F: Check-in + prioridade
  F->>M: Chamada / consulta
  M->>M: PCE (SOAP, diagnóstico)
  opt Pedido analítico
    M->>L: Pedido lab
    L->>L: Colheita → resultado → validação
    L->>M: Publicação
  end
  opt Cobrança
    R->>B: Orçamento / fatura
    B->>B: Pagamento + recibo
  end
```

---

## 2. Perfis e módulos SGCS (Sprint 14)

```mermaid
flowchart TB
  subgraph Perfis
    ADM[Administrador]
    DIR[Director]
    REC[Rececionista]
    MED[Médico]
    LAB[Técnico Lab]
  end

  subgraph Modulos
    PAT[Pacientes]
    REP[Receção]
    APT[Consultas / PCE]
    DOC[Módulo médico]
    LABM[Laboratório]
    BIL[Faturação]
    FIN[Financeiro]
    REP2[Relatórios]
    NOT[Notificações]
    CFG[Configurações]
  end

  REC --> PAT & REP & APT & BIL
  MED --> APT & DOC & LABM
  LAB --> LABM
  DIR --> BIL & FIN & REP2
  ADM --> CFG
```

---

## 3. Expansão planeada (não implementada)

```mermaid
flowchart LR
  subgraph v14[v1.4]
    ENF[Enfermagem]
    TRI[Triagem]
  end
  subgraph v15[v1.5]
    IMG[Imagiologia]
    IMM[Imunologia / lab+]
  end
  subgraph v16_19[v1.6 - v1.9]
    FAR[Farmácia]
    CIR[Cirurgia]
    MAT[Maternidade]
    INT[Internamento]
  end

  REP[Receção actual] --> ENF
  ENF --> TRI
  APT[Consultas] --> IMG
  APT --> FAR
  APT --> CIR
  MAT --> INT
```

---

## 4. Dados de configuração (Sprint 15)

```mermaid
flowchart LR
  JSON[data/clinic/*.json]
  CSV[catalogo_servicos_sauvida.csv]
  CMD1[seed_clinic_initial]
  CMD2[import_servico_catalog]
  DB[(PostgreSQL)]

  JSON --> CMD1 --> DB
  CSV --> CMD2 --> DB
  CMD1 --> CMD2
```

---

*Diagramas em Mermaid — renderizam no GitHub e em editores compatíveis.*
