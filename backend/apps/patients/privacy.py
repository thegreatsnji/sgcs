"""Regras de privacidade clínica vs administrativa (Receção)."""

from apps.authentication.models import UserRole
from apps.patients.constants import HistoryEventType, PatientDocumentType
from apps.users.services.rbac_service import RBACService

# Conteúdo clínico detalhado — exige appointments.clinical (Médico/Admin).
CLINICAL_CONTENT_PERMISSION = "appointments.clinical"

# Eventos de PatientHistory cujo detalhe não deve ir para o balcão.
CLINICAL_HISTORY_EVENT_TYPES = frozenset(
    {
        HistoryEventType.DIAGNOSTICO,
        HistoryEventType.MEDICACAO,
        HistoryEventType.CIRURGIA,
        HistoryEventType.ALERGIA,
        HistoryEventType.DOENCA_CRONICA,
        HistoryEventType.EXAME,
        HistoryEventType.OBSERVACAO,
        HistoryEventType.ADMISSAO,
        HistoryEventType.ALTA,
    }
)

# Documentos do utente com conteúdo clínico sensível.
CLINICAL_DOCUMENT_TYPES = frozenset(
    {
        PatientDocumentType.EXAME_EXTERNO,
    }
)

# Campos de consulta ocultos à Receção / quem não tem clinical.
APPOINTMENT_CLINICAL_FIELDS = frozenset(
    {
        "diagnosis",
        "clinical_notes",
        "notes",
    }
)

REDACTED_HISTORY_DESCRIPTION = "Registo clínico — detalhe reservado à equipa clínica."


def user_can_access_clinical_content(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser or getattr(user, "role", None) == UserRole.ADMINISTRADOR:
        return True
    return RBACService.user_has_permission(user, CLINICAL_CONTENT_PERMISSION)


def user_is_receptionist(user) -> bool:
    return bool(user and getattr(user, "role", None) == UserRole.RECECIONISTA)
