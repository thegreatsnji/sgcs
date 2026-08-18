"""Constantes da migração histórica SauVida (Sprint 21 Fase 1)."""

from pathlib import Path

FONTE_MIGRACAO = "MIGRACAO_EXCEL_SAUVIDA"
CREATED_VIA = "import_sauvida_history"
RECORD_CLASS_HISTORICO = "HISTORICO_IMPORTADO"
RECORD_CLASS_OPERACAO = "OPERACAO_SGCS"
BATCH_INITIAL = "SAUVIDA-HIST-V1"
BATCH_REVIEW = "SAUVIDA-HIST-V1-REVIEW"

PATIENT_REVIEW_IMPORT = {"PESSOAS_DIFERENTES", "IMPORTAR_SEPARADAMENTE"}
PATIENT_REVIEW_SKIP = {"NAO_IMPORTAR", "NÃO_IMPORTAR", "INDETERMINADO"}
PATIENT_REVIEW_MERGE = "MESMA_PESSOA"
DATE_REVIEW_ACCEPT = {"ACEITAR", "CONFIRMADA", "OK", "CONFIRMAR_DATA", "CORRIGIR_DATA"}
DATE_REVIEW_REJECT = {"NAO_IMPORTAR", "NÃO_IMPORTAR", "INDETERMINADO"}
LAB_REVIEW_UNLOCK = {"CONFIRMAR_MAPEAMENTO", "MANTER_TEXTUAL", "OUTRO_EXAME"}
LAB_REVIEW_MAPPED = {"CONFIRMAR_MAPEAMENTO", "OUTRO_EXAME"}
DOCTOR_REVIEW_MAP = "MAPEAR_COM_MEDICO_SGCS"
DOCTOR_REVIEW_KEEP = "MANTER_NOME_HISTORICO"

VERIFICATION_IMPORTED = "IMPORTADO_NAO_VERIFICADO"
VERIFICATION_VERIFIED = "VERIFICADO"
VERIFICATION_NEEDS_REVIEW = "NECESSITA_REVISAO"
VERIFICATION_BLOCKED_DUP = "BLOQUEADO_DUPLICADO"

PRIORITY_CRITICAL = "CRITICA"
PRIORITY_HIGH = "ALTA"
PRIORITY_MEDIUM = "MEDIA"
PRIORITY_LOW = "BAIXA"
PRIORITY_INFO = "INFORMATIVA"

EXPECTED_DATE_MIN = "2010-01-01"
EXPECTED_DATE_MAX_OFFSET_DAYS = 1

EXCEL_ERRORS = (
    "#REF!",
    "#VALUE!",
    "#N/A",
    "#DIV/0!",
    "#NAME?",
    "#NULL!",
    "#NUM!",
    "#GETTING_DATA!",
)

SHEET_TYPES = {
    "LABORATORIO": "LABORATORIO",
    "CONSULTA": "CONSULTA",
    "CONTROLO": "CONTROLO",
    "ECOGRAFIA": "ECOGRAFIA",
    "CIRURGIA": "CIRURGIA",
    "STOCK_MEDICAMENTO": "STOCK_MEDICAMENTO",
    "STOCK_MATERIAL": "STOCK_MATERIAL",
    "RESUMO_FINANCEIRO": "RESUMO_FINANCEIRO",
    "OUTRO": "OUTRO",
}

EVENT_TYPES = ("CONSULTA", "CONTROLO", "LABORATORIO", "ECOGRAFIA", "CIRURGIA", "OUTRO")

PATIENT_STATES = ("PRONTO", "REVISAR", "DUPLICADO_POSSIVEL", "DADOS_INSUFICIENTES")

DUPLICATE_DECISIONS = {
    "A": "PROVAVEL_MESMO_PACIENTE",
    "B": "REVISAR_DUPLICADO",
    "C": "POSSIVEL_DUPLICADO",
}

MAP_STATES = ("ALINHADO", "POSSIVEL", "AMBIGUO", "SEM_CORRESPONDENCIA", "REVISAR")

STOCK_TYPES = ("MEDICAMENTO", "MATERIAL_CLINICO", "PROCEDIMENTO", "OUTRO")

NON_STOCK_KEYWORDS = (
    "cama",
    "mao de obra",
    "mao-de-obra",
    "mao deobra",
    "sutura de ferida",
    "sutura",
    "consulta",
    "ecografia",
    "cirurgia",
    "taxa",
    "internamento",
)

SKIP_ROW_KEYWORDS = (
    "total",
    "subtotal",
    "resumo",
    "soma",
    "geral",
    "pagina",
    "página",
)

HEADER_ALIASES = {
    "nome": ("nome", "paciente", "nome do paciente", "nome completo", "utente", "cliente"),
    "telefone": (
        "telefone",
        "telemovel",
        "telemóvel",
        "n telemovel",
        "no telemovel",
        "nº telemovel",
        "contacto",
        "celular",
        "telf",
        "phone",
    ),
    "data_nascimento": ("data nascimento", "data de nascimento", "dn", "nascimento", "d.nasc"),
    "idade": ("idade", "anos"),
    "sexo": ("sexo", "genero", "género", "genero "),
    "residencia": ("residencia", "residência", "morada", "endereco", "endereço", "bairro"),
    "processo": ("processo", "n processo", "n. processo", "numero processo", "nº processo", "n.º processo"),
    "data": ("data", "data consulta", "data exame", "dia", "data acto", "data ato"),
    "medico": (
        "medico",
        "médico",
        "nome de medico",
        "nome do medico",
        "nome de médico",
        "doutor",
        "profissional",
    ),
    "tipo_operacao": ("tipo de operacao", "tipo de operação", "tipo operacao", "tipo operação"),
    "descricao": (
        "servico",
        "serviço",
        "exame",
        "descricao",
        "descrição",
        "acto",
        "ato",
        "procedimento",
        "designacao",
        "designação",
        "produto",
        "artigo",
        "medicamento",
        "material",
        "item",
    ),
    "preco": ("preco", "preço", "valor", "pvp", "preco unitario", "preço unitário", "montante"),
    "desconto": ("desconto",),
    "valor_liquido": ("liquido", "líquido", "valor liquido", "valor líquido", "pago", "total linha"),
    "quantidade": ("quantidade", "qtd", "qty", "unid"),
    "unidade": ("unidade",),
}

CONSULTATION_CANONICAL = (
    ("consulta geral", "CONSULTA_GERAL", "CONS-CLIN-GER"),
    ("clinica geral", "CONSULTA_GERAL", "CONS-CLIN-GER"),
    ("clínico geral", "CONSULTA_GERAL", "CONS-CLIN-GER"),
    ("clinico geral", "CONSULTA_GERAL", "CONS-CLIN-GER"),
    ("coonsulta geral", "CONSULTA_GERAL", "CONS-CLIN-GER"),
    ("controle", "CONTROLO", "CONS-CONTROLO"),
    ("controlo", "CONTROLO", "CONS-CONTROLO"),
    ("especialidade", "CONSULTA_ESPECIALIDADE", "CONS-ESP"),
    ("pre natal", "CONSULTA_PRE_NATAL", "CONS-PRE-NATAL"),
    ("pré-natal", "CONSULTA_PRE_NATAL", "CONS-PRE-NATAL"),
    ("prenatal", "CONSULTA_PRE_NATAL", "CONS-PRE-NATAL"),
    ("pediatr", "CONSULTA_PEDIATRICA", "CONS-ESP"),
)

NAME_PARTICLES = frozenset({"da", "de", "do", "das", "dos", "e", "del", "di"})

AUTO_MAP_MIN_CONFIDENCE = 0.92
POSSIBLE_MAP_MIN_CONFIDENCE = 0.80
NAME_FUZZY_MIN = 0.85
NAME_PROBABLE_MIN = 0.92

DEFAULT_OUTPUT_RELATIVE = Path("backend/data/private/sauvida_migration")
DEFAULT_CATALOG_RELATIVE = Path("backend/data/releases/catalogo_sauvida_v1.csv")
DEFAULT_EXAMS_RELATIVE = Path("backend/data/releases/exames_laboratoriais_sauvida_v1.csv")
