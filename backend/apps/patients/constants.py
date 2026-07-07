"""Constantes e enums do módulo de pacientes."""

from django.db import models


class DocumentType(models.TextChoices):
    BI = "BI", "Bilhete de Identidade"
    PASSAPORTE = "PASSAPORTE", "Passaporte"
    CARTAO_RESIDENTE = "CARTAO_RESIDENTE", "Cartão de residente"
    OUTRO = "OUTRO", "Outro"


class PatientGender(models.TextChoices):
    MASCULINO = "M", "Masculino"
    FEMININO = "F", "Feminino"
    OUTRO = "O", "Outro"


class BloodType(models.TextChoices):
    A_POS = "A+", "A+"
    A_NEG = "A-", "A-"
    B_POS = "B+", "B+"
    B_NEG = "B-", "B-"
    AB_POS = "AB+", "AB+"
    AB_NEG = "AB-", "AB-"
    O_POS = "O+", "O+"
    O_NEG = "O-", "O-"
    DESCONHECIDO = "DESCONHECIDO", "Desconhecido"


class MaritalStatus(models.TextChoices):
    SOLTEIRO = "SOLTEIRO", "Solteiro"
    CASADO = "CASADO", "Casado"
    DIVORCIADO = "DIVORCIADO", "Divorciado"
    VIUVO = "VIUVO", "Viúvo"
    OUTRO = "OUTRO", "Outro"


class EmergencyRelationship(models.TextChoices):
    CONJUGE = "CONJUGE", "Cônjuge"
    PAI = "PAI", "Pai"
    MAE = "MAE", "Mãe"
    FILHO = "FILHO", "Filho"
    IRMAO = "IRMAO", "Irmão"
    AMIGO = "AMIGO", "Amigo"
    OUTRO = "OUTRO", "Outro"


class InsurancePlanType(models.TextChoices):
    BASICO = "BASICO", "Básico"
    COMPLETO = "COMPLETO", "Completo"
    EMPRESA = "EMPRESA", "Empresa"
    ESTADO = "ESTADO", "Estado"
    OUTRO = "OUTRO", "Outro"


class AllergySeverity(models.TextChoices):
    LEVE = "LEVE", "Leve"
    MODERADA = "MODERADA", "Moderada"
    GRAVE = "GRAVE", "Grave"
    ANAFILAXIA = "ANAFILAXIA", "Anafilaxia"


class ChronicDiseaseStatus(models.TextChoices):
    ATIVA = "ATIVA", "Ativa"
    CONTROLADA = "CONTROLADA", "Controlada"
    REMISSAO = "REMISSAO", "Remissão"
    CURADA = "CURADA", "Curada"


class PatientDocumentType(models.TextChoices):
    BI = "BI", "Bilhete de Identidade"
    PASSAPORTE = "PASSAPORTE", "Passaporte"
    CARTAO_SEGURO = "CARTAO_SEGURO", "Cartão de seguro"
    CONSENTIMENTO = "CONSENTIMENTO", "Consentimento"
    EXAME_EXTERNO = "EXAME_EXTERNO", "Exame externo"
    DECLARACAO = "DECLARACAO", "Declaração"
    OUTRO = "OUTRO", "Outro"


class HistoryEventType(models.TextChoices):
    REGISTO = "REGISTO", "Registo"
    ADMISSAO = "ADMISSAO", "Admissão"
    ALTA = "ALTA", "Alta"
    CONSULTA = "CONSULTA", "Consulta"
    EXAME = "EXAME", "Exame"
    DIAGNOSTICO = "DIAGNOSTICO", "Diagnóstico"
    CIRURGIA = "CIRURGIA", "Cirurgia"
    MEDICACAO = "MEDICACAO", "Medicação"
    ALERGIA = "ALERGIA", "Alergia"
    DOENCA_CRONICA = "DOENCA_CRONICA", "Doença crónica"
    DOCUMENTO = "DOCUMENTO", "Documento"
    OBSERVACAO = "OBSERVACAO", "Observação"
    PAGAMENTO = "PAGAMENTO", "Pagamento"
    OUTRO = "OUTRO", "Outro"


class ObservationType(models.TextChoices):
    CLINICA = "CLINICA", "Clínica"
    ENFERMAGEM = "ENFERMAGEM", "Enfermagem"
    ADMINISTRATIVA = "ADMINISTRATIVA", "Administrativa"
