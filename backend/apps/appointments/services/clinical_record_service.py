"""Serviço do Prontuário Clínico Eletrónico (PCE)."""

from django.db import transaction
from django.db.models import Prefetch

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import (
    AnotacaoClinica,
    Appointment,
    Diagnostico,
    PedidoImagiologia,
    PedidoLaboratorio,
    Seguimento,
    SinaisVitais,
)
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.patients.models import PatientAllergy, PatientChronicDisease


class ClinicalRecordService:
    @staticmethod
    def _log(action, user, request, appointment, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="appointment",
            resource_id=str(appointment.pk),
            metadata=metadata or {"patient_id": appointment.patient_id},
        )

    @staticmethod
    def _ensure_doctor(user) -> None:
        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return
        if user.role != UserRole.MEDICO:
            raise ValueError("Apenas médicos podem preencher o prontuário clínico.")

    @staticmethod
    def _get_appointment(appointment_id: int) -> Appointment:
        return (
            Appointment.objects.select_related(
                "patient",
                "doctor",
                "sinais_vitais",
                "anotacao_soap",
                "seguimento",
            )
            .prefetch_related(
                Prefetch(
                    "patient__allergies",
                    queryset=PatientAllergy.objects.filter(is_active=True),
                ),
                Prefetch(
                    "patient__chronic_diseases",
                    queryset=PatientChronicDisease.objects.filter(is_active=True),
                ),
                "diagnosticos",
                "pedidos_laboratorio",
                "pedidos_imagiologia",
            )
            .get(pk=appointment_id)
        )

    @staticmethod
    def _ensure_editable(appointment: Appointment, user) -> None:
        ClinicalRecordService._ensure_doctor(user)
        if appointment.status != AppointmentStatus.EM_CONSULTA:
            raise ValueError("A consulta deve estar em curso para editar o prontuário.")
        if (
            appointment.doctor_id
            and appointment.doctor_id != user.pk
            and user.role == UserRole.MEDICO
            and not user.is_superuser
        ):
            raise ValueError("Apenas o médico responsável pode editar o prontuário.")

    @staticmethod
    def _patient_context(patient, request=None) -> dict:
        photo = (
            patient.photos.filter(is_primary=True, is_active=True)
            .select_related("stored_file")
            .first()
        )
        photo_url = None
        if photo and photo.stored_file and photo.stored_file.file:
            photo_url = (
                request.build_absolute_uri(photo.stored_file.file.url)
                if request
                else photo.stored_file.file.url
            )
        return {
            "id": patient.pk,
            "full_name": patient.full_name,
            "patient_number": patient.patient_number,
            "age": patient.age,
            "gender": patient.gender,
            "blood_type": patient.blood_type or "",
            "phone": patient.phone,
            "email": patient.email,
            "photo_url": photo_url,
            "allergies": [
                {
                    "id": a.pk,
                    "allergen": a.allergen,
                    "severity": a.severity,
                    "reaction": a.reaction,
                }
                for a in patient.allergies.all()
            ],
            "chronic_diseases": [
                {
                    "id": d.pk,
                    "disease_name": d.disease_name,
                    "icd_code": d.icd_code,
                    "status": d.status,
                }
                for d in patient.chronic_diseases.all()
            ],
        }

    @staticmethod
    def _ultimas_consultas(patient_id: int, exclude_id: int | None = None, limit: int = 5):
        qs = (
            Appointment.objects.filter(patient_id=patient_id)
            .exclude(pk=exclude_id)
            .select_related("doctor")
            .order_by("-scheduled_at")[:limit]
        )
        return [
            {
                "id": a.pk,
                "appointment_number": a.appointment_number,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
                "doctor": a.doctor.get_full_name() if a.doctor else None,
                "diagnosis": a.diagnosis,
            }
            for a in qs
        ]

    @staticmethod
    def _ultimos_pedidos_laboratorio(patient_id: int, limit: int = 5):
        return list(
            PedidoLaboratorio.objects.filter(consulta__patient_id=patient_id)
            .select_related("consulta")
            .order_by("-created_at")[:limit]
            .values(
                "id",
                "tipo_exame",
                "estado",
                "prioridade",
                "created_at",
                "consulta__appointment_number",
            )
        )

    @staticmethod
    def _ultimos_pedidos_imagiologia(patient_id: int, limit: int = 5):
        return list(
            PedidoImagiologia.objects.filter(consulta__patient_id=patient_id)
            .select_related("consulta")
            .order_by("-created_at")[:limit]
            .values(
                "id",
                "tipo_exame",
                "estado",
                "prioridade",
                "created_at",
                "consulta__appointment_number",
            )
        )

    @staticmethod
    def obter_prontuario(appointment_id: int, request=None) -> dict:
        appointment = ClinicalRecordService._get_appointment(appointment_id)
        patient = appointment.patient

        sinais = getattr(appointment, "sinais_vitais", None)
        soap = getattr(appointment, "anotacao_soap", None)
        seguimento = getattr(appointment, "seguimento", None)

        return {
            "consulta": {
                "id": appointment.pk,
                "appointment_number": appointment.appointment_number,
                "status": appointment.status,
                "chief_complaint": appointment.chief_complaint,
                "notes": appointment.notes,
                "diagnosis": appointment.diagnosis,
                "clinical_notes": appointment.clinical_notes,
                "started_at": appointment.started_at.isoformat() if appointment.started_at else None,
                "editavel": appointment.is_clinical_editable,
            },
            "paciente": ClinicalRecordService._patient_context(patient, request=request),
            "sinais_vitais": ClinicalRecordService._serialize_sinais(sinais) if sinais else None,
            "anotacao_soap": ClinicalRecordService._serialize_soap(soap) if soap else None,
            "diagnosticos": [
                ClinicalRecordService._serialize_diagnostico(d)
                for d in appointment.diagnosticos.all()
            ],
            "pedidos_laboratorio": [
                ClinicalRecordService._serialize_pedido_lab(p)
                for p in appointment.pedidos_laboratorio.all()
            ],
            "resultados_laboratoriais": ClinicalRecordService._resultados_laboratoriais_consulta(
                appointment.pk,
                request=request,
            ),
            "pedidos_imagiologia": [
                ClinicalRecordService._serialize_pedido_img(p)
                for p in appointment.pedidos_imagiologia.all()
            ],
            "seguimento": (
                ClinicalRecordService._serialize_seguimento(seguimento) if seguimento else None
            ),
            "ultimas_consultas": ClinicalRecordService._ultimas_consultas(
                patient.pk,
                exclude_id=appointment.pk,
            ),
            "ultimos_pedidos_laboratorio": ClinicalRecordService._ultimos_pedidos_laboratorio(
                patient.pk
            ),
            "ultimos_pedidos_imagiologia": ClinicalRecordService._ultimos_pedidos_imagiologia(
                patient.pk
            ),
        }

    @staticmethod
    def _serialize_sinais(obj: SinaisVitais) -> dict:
        return {
            "id": obj.pk,
            "pressao_arterial": obj.pressao_arterial,
            "frequencia_cardiaca": obj.frequencia_cardiaca,
            "frequencia_respiratoria": obj.frequencia_respiratoria,
            "temperatura": float(obj.temperatura) if obj.temperatura is not None else None,
            "saturacao_oxigenio": obj.saturacao_oxigenio,
            "peso": float(obj.peso) if obj.peso is not None else None,
            "altura": float(obj.altura) if obj.altura is not None else None,
            "imc": float(obj.imc) if obj.imc is not None else None,
            "observacoes": obj.observacoes,
        }

    @staticmethod
    def _serialize_soap(obj: AnotacaoClinica) -> dict:
        return {
            "id": obj.pk,
            "subjetivo": obj.subjetivo,
            "objetivo": obj.objetivo,
            "avaliacao": obj.avaliacao,
            "plano": obj.plano,
        }

    @staticmethod
    def _serialize_diagnostico(obj: Diagnostico) -> dict:
        return {
            "id": obj.pk,
            "codigo_cid10": obj.codigo_cid10,
            "descricao": obj.descricao,
            "tipo": obj.tipo,
        }

    @staticmethod
    def _serialize_pedido_lab(obj: PedidoLaboratorio) -> dict:
        return {
            "id": obj.pk,
            "tipo_exame": obj.tipo_exame,
            "prioridade": obj.prioridade,
            "observacoes": obj.observacoes,
            "estado": obj.estado,
            "created_at": obj.created_at.isoformat(),
        }

    @staticmethod
    def _serialize_resultado_lab(obj, request=None) -> dict:
        anexos = []
        for anexo in obj.anexos.all():
            url = None
            if anexo.ficheiro and anexo.ficheiro.file:
                url = (
                    request.build_absolute_uri(anexo.ficheiro.file.url)
                    if request
                    else anexo.ficheiro.file.url
                )
            anexos.append(
                {
                    "id": anexo.pk,
                    "tipo": anexo.tipo,
                    "descricao": anexo.descricao,
                    "nome_ficheiro": anexo.ficheiro.name if anexo.ficheiro else "",
                    "ficheiro_url": url,
                }
            )
        return {
            "id": obj.pk,
            "pedido_laboratorial_id": obj.pedido_laboratorial_id,
            "numero_pedido": obj.pedido_laboratorial.numero_pedido,
            "estado": obj.estado,
            "data_resultado": obj.data_resultado.isoformat() if obj.data_resultado else None,
            "data_validacao": obj.data_validacao.isoformat() if obj.data_validacao else None,
            "responsavel": obj.responsavel.get_full_name() if obj.responsavel else None,
            "conclusao": obj.conclusao,
            "observacoes": obj.observacoes,
            "parametros": [
                {
                    "id": p.pk,
                    "nome": p.nome,
                    "valor": p.valor,
                    "unidade": p.unidade,
                    "valor_minimo": p.valor_minimo,
                    "valor_maximo": p.valor_maximo,
                    "interpretacao": p.interpretacao,
                }
                for p in obj.parametros.all()
            ],
            "anexos": anexos,
        }

    @staticmethod
    def _resultados_laboratoriais_consulta(appointment_id: int, request=None) -> list:
        from apps.laboratory.models import ResultadoLaboratorial

        qs = (
            ResultadoLaboratorial.objects.filter(pedido_laboratorial__consulta_id=appointment_id)
            .select_related("pedido_laboratorial", "responsavel")
            .prefetch_related("parametros", "anexos__ficheiro")
            .order_by("-data_resultado")
        )
        return [ClinicalRecordService._serialize_resultado_lab(r, request) for r in qs]

    @staticmethod
    def _serialize_pedido_img(obj: PedidoImagiologia) -> dict:
        return {
            "id": obj.pk,
            "tipo_exame": obj.tipo_exame,
            "prioridade": obj.prioridade,
            "observacoes": obj.observacoes,
            "estado": obj.estado,
            "created_at": obj.created_at.isoformat(),
        }

    @staticmethod
    def _serialize_seguimento(obj: Seguimento) -> dict:
        return {
            "id": obj.pk,
            "data_retorno": obj.data_retorno.isoformat(),
            "motivo": obj.motivo,
            "observacoes": obj.observacoes,
        }

    @staticmethod
    @transaction.atomic
    def actualizar_campos_legados(
        appointment_id: int,
        user,
        *,
        chief_complaint: str | None = None,
        notes: str | None = None,
        diagnosis: str | None = None,
        clinical_notes: str | None = None,
        request=None,
    ) -> Appointment:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        update_fields = ["updated_at"]
        if chief_complaint is not None:
            appointment.chief_complaint = chief_complaint
            update_fields.append("chief_complaint")
        if notes is not None:
            appointment.notes = notes
            update_fields.append("notes")
        if diagnosis is not None:
            appointment.diagnosis = diagnosis
            update_fields.append("diagnosis")
        if clinical_notes is not None:
            appointment.clinical_notes = clinical_notes
            update_fields.append("clinical_notes")

        appointment.save(update_fields=update_fields)
        ClinicalRecordService._log(
            AuditAction.CONSULTA_CLINICA_EDITADA,
            user,
            request,
            appointment,
            f"Prontuário actualizado — {appointment.patient.full_name}.",
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def guardar_sinais_vitais(appointment_id: int, user, data: dict, request=None) -> SinaisVitais:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        sinais, _ = SinaisVitais.objects.get_or_create(consulta=appointment)
        for field in (
            "pressao_arterial",
            "frequencia_cardiaca",
            "frequencia_respiratoria",
            "temperatura",
            "saturacao_oxigenio",
            "peso",
            "altura",
            "observacoes",
        ):
            if field in data:
                setattr(sinais, field, data[field])
        sinais.registado_por = user
        sinais.save()

        ClinicalRecordService._log(
            AuditAction.SINAIS_VITAIS_REGISTADOS,
            user,
            request,
            appointment,
            f"Sinais vitais registados — {appointment.patient.full_name}.",
            metadata={"imc": float(sinais.imc) if sinais.imc else None},
        )
        return sinais

    @staticmethod
    @transaction.atomic
    def guardar_soap(appointment_id: int, user, data: dict, request=None) -> AnotacaoClinica:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        soap, _ = AnotacaoClinica.objects.get_or_create(consulta=appointment)
        for field in ("subjetivo", "objetivo", "avaliacao", "plano"):
            if field in data:
                setattr(soap, field, data[field])
        soap.registado_por = user
        soap.save()

        ClinicalRecordService._log(
            AuditAction.CONSULTA_CLINICA_EDITADA,
            user,
            request,
            appointment,
            f"Anotação SOAP actualizada — {appointment.patient.full_name}.",
            metadata={"section": "soap"},
        )
        return soap

    @staticmethod
    @transaction.atomic
    def adicionar_diagnostico(appointment_id: int, user, data: dict, request=None) -> Diagnostico:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        diagnostico = Diagnostico.objects.create(
            consulta=appointment,
            codigo_cid10=data["codigo_cid10"],
            descricao=data["descricao"],
            tipo=data.get("tipo", "PRINCIPAL"),
            registado_por=user,
        )

        if diagnostico.tipo == "PRINCIPAL" and not appointment.diagnosis:
            appointment.diagnosis = f"{diagnostico.codigo_cid10} — {diagnostico.descricao}"
            appointment.save(update_fields=["diagnosis", "updated_at"])

        ClinicalRecordService._log(
            AuditAction.DIAGNOSTICO_ADICIONADO,
            user,
            request,
            appointment,
            f"Diagnóstico {diagnostico.codigo_cid10} adicionado.",
            metadata={"diagnostico_id": diagnostico.pk},
        )
        return diagnostico

    @staticmethod
    @transaction.atomic
    def adicionar_pedido_laboratorio(
        appointment_id: int,
        user,
        data: dict,
        request=None,
    ) -> PedidoLaboratorio:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        pedido = PedidoLaboratorio.objects.create(
            consulta=appointment,
            tipo_exame=data["tipo_exame"],
            prioridade=data.get("prioridade", "NORMAL"),
            observacoes=data.get("observacoes", ""),
            solicitado_por=user,
        )
        ClinicalRecordService._log(
            AuditAction.PEDIDO_LABORATORIO,
            user,
            request,
            appointment,
            f"Pedido de laboratório: {pedido.tipo_exame}.",
            metadata={"pedido_id": pedido.pk},
        )

        from apps.laboratory.services.laboratory_service import LaboratoryService

        LaboratoryService.criar_de_pedido_consulta(pedido, user=user)
        return pedido

    @staticmethod
    @transaction.atomic
    def adicionar_pedido_imagiologia(
        appointment_id: int,
        user,
        data: dict,
        request=None,
    ) -> PedidoImagiologia:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        pedido = PedidoImagiologia.objects.create(
            consulta=appointment,
            tipo_exame=data["tipo_exame"],
            prioridade=data.get("prioridade", "NORMAL"),
            observacoes=data.get("observacoes", ""),
            solicitado_por=user,
        )
        ClinicalRecordService._log(
            AuditAction.PEDIDO_IMAGIOLOGIA,
            user,
            request,
            appointment,
            f"Pedido de imagiologia: {pedido.tipo_exame}.",
            metadata={"pedido_id": pedido.pk},
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def guardar_seguimento(appointment_id: int, user, data: dict, request=None) -> Seguimento:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(
            pk=appointment_id
        )
        ClinicalRecordService._ensure_editable(appointment, user)

        seguimento, _ = Seguimento.objects.update_or_create(
            consulta=appointment,
            defaults={
                "data_retorno": data["data_retorno"],
                "motivo": data["motivo"],
                "observacoes": data.get("observacoes", ""),
                "registado_por": user,
            },
        )

        ClinicalRecordService._log(
            AuditAction.SEGUIMENTO_AGENDADO,
            user,
            request,
            appointment,
            f"Seguimento agendado para {seguimento.data_retorno:%d/%m/%Y}.",
            metadata={"data_retorno": seguimento.data_retorno.isoformat()},
        )
        return seguimento
