"""Âmbito operacional da Clínica SauVida — categorias/departamentos não aplicáveis."""

# Mantidos no modelo para compatibilidade futura; excluídos de import e UI operacional.
EXCLUDED_SERVICE_CATEGORIES = frozenset({"INTERNAMENTO"})
EXCLUDED_DEPARTMENT_CODES = frozenset({"INT"})
# Códigos de serviço não aplicáveis à operação SauVida (farmácia comercial, etc.)
EXCLUDED_SERVICE_CODES = frozenset({"OUT-FARM-MARGEM"})
