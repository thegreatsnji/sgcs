"""Serviço de resultados laboratoriais."""

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.laboratory.constants import (
    ALLOWED_ATTACHMENT_MIMES,
    InterpretacaoParametro,
    PedidoLaboratorialEstado,
    ResultadoLaboratorialEstado,
    TipoAnexoResultado,
)
from apps.laboratory.models import (
    AnexoResultado,
    ParametroResultado,
    PedidoLaboratorial,
    ResultadoLaboratorial,
)
from apps.laboratory.services.cache_service import LaboratoryCacheService
from apps.patients.constants import HistoryEventType
from apps.patients.services.history_service import PatientHistoryService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class LaboratoryResultService:
    @staticmethod
    def _log(action, user, request, resultado, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="laboratory_result",
            resource_id=str(resultado.pk),
            metadata=metadata
            or {
                "pedido_id": resultado.pedido_laboratorial_id,
                "numero_pedido": resultado.pedido_laboratorial.numero_pedido,
            },
        )

    @staticmethod
    def _ensure_laboratorio(user) -> None:
        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return
        if user.role != UserRole.LABORATORIO:
            raise ValueError("Apenas utilizadores de laboratório podem efectuar esta acção.")

    @staticmethod
    def _calcular_interpretacao(valor: str, minimo: str, maximo: str) -> str:
        if not valor or not minimo or not maximo:
            return InterpretacaoParametro.NORMAL
        try:
            v = Decimal(str(valor).replace(",", "."))
            lo = Decimal(str(minimo).replace(",", "."))
            hi = Decimal(str(maximo).replace(",", "."))
        except (InvalidOperation, ValueError):
            return InterpretacaoParametro.NORMAL
        if v < lo:
            return InterpretacaoParametro.BAIXO
        if v > hi:
            return InterpretacaoParametro.ALTO
        return InterpretacaoParametro.NORMAL

    @staticmethod
    def listar_resultados():
        return (
            ResultadoLaboratorial.objects.select_related(
                "pedido_laboratorial",
                "pedido_laboratorial__paciente",
                "pedido_laboratorial__medico",
                "responsavel",
                "validado_por",
            )
            .prefetch_related("parametros", "anexos__ficheiro")
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def criar_resultado(pedido_id: int, user, *, observacoes: str = "", conclusao: str = "", request=None):
        LaboratoryResultService._ensure_laboratorio(user)
        pedido = PedidoLaboratorial.objects.select_for_update().select_related("consulta", "paciente").get(
            pk=pedido_id
        )
        if pedido.estado not in {
            PedidoLaboratorialEstado.EM_PROCESSAMENTO,
            PedidoLaboratorialEstado.CONCLUIDO,
        }:
            raise ValueError("O pedido deve estar em processamento para registar resultados.")
        if hasattr(pedido, "resultado"):
            raise ValueError("Já existe um resultado para este pedido.")

        now = timezone.now()
        resultado = ResultadoLaboratorial.objects.create(
            pedido_laboratorial=pedido,
            estado=ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
            responsavel=user,
            data_resultado=now,
            observacoes=observacoes,
            conclusao=conclusao,
        )
        LaboratoryResultService._log(
            AuditAction.RESULTADO_CRIADO,
            user,
            request,
            resultado,
            f"Resultado criado para o pedido {pedido.numero_pedido}.",
        )
        LaboratoryCacheService.invalidate_all(patient_id=pedido.paciente_id, consulta_id=pedido.consulta_id)
        return resultado

    @staticmethod
    @transaction.atomic
    def editar_resultado(
        resultado_id: int,
        user,
        *,
        observacoes: str | None = None,
        conclusao: str | None = None,
        request=None,
    ):
        LaboratoryResultService._ensure_laboratorio(user)
        resultado = (
            ResultadoLaboratorial.objects.select_for_update()
            .select_related("pedido_laboratorial")
            .get(pk=resultado_id)
        )
        if not resultado.is_editavel:
            raise ValueError("Não é possível alterar um resultado já validado.")

        update_fields = ["updated_at"]
        if observacoes is not None:
            resultado.observacoes = observacoes
            update_fields.append("observacoes")
        if conclusao is not None:
            resultado.conclusao = conclusao
            update_fields.append("conclusao")
        resultado.save(update_fields=update_fields)

        LaboratoryResultService._log(
            AuditAction.RESULTADO_EDITADO,
            user,
            request,
            resultado,
            f"Resultado editado — pedido {resultado.pedido_laboratorial.numero_pedido}.",
        )
        pedido = resultado.pedido_laboratorial
        LaboratoryCacheService.invalidate_all(patient_id=pedido.paciente_id, consulta_id=pedido.consulta_id)
        return resultado

    @staticmethod
    @transaction.atomic
    def adicionar_parametro(resultado_id: int, user, data: dict, request=None):
        LaboratoryResultService._ensure_laboratorio(user)
        resultado = (
            ResultadoLaboratorial.objects.select_for_update()
            .select_related("pedido_laboratorial")
            .get(pk=resultado_id)
        )
        if not resultado.is_editavel:
            raise ValueError("Não é possível alterar parâmetros de um resultado validado.")

        interpretacao = data.get("interpretacao") or LaboratoryResultService._calcular_interpretacao(
            data.get("valor", ""),
            data.get("valor_minimo", ""),
            data.get("valor_maximo", ""),
        )
        parametro = ParametroResultado.objects.create(
            resultado=resultado,
            nome=data["nome"],
            valor=data["valor"],
            unidade=data.get("unidade", ""),
            valor_minimo=data.get("valor_minimo", ""),
            valor_maximo=data.get("valor_maximo", ""),
            interpretacao=interpretacao,
            ordem=data.get("ordem", 0),
        )
        resultado.estado = ResultadoLaboratorialEstado.RESULTADO_PENDENTE
        resultado.save(update_fields=["estado", "updated_at"])
        return parametro

    @staticmethod
    @transaction.atomic
    def validar_resultado(resultado_id: int, user, request=None):
        if not user.is_superuser and user.role not in {UserRole.ADMINISTRADOR, UserRole.LABORATORIO}:
            raise ValueError("Sem permissão para validar resultados.")

        resultado = (
            ResultadoLaboratorial.objects.select_for_update()
            .select_related("pedido_laboratorial", "pedido_laboratorial__consulta", "pedido_laboratorial__paciente")
            .get(pk=resultado_id)
        )
        if resultado.estado not in {
            ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
            ResultadoLaboratorialEstado.EM_PROCESSAMENTO,
        }:
            raise ValueError("Apenas resultados pendentes podem ser validados.")

        now = timezone.now()
        resultado.estado = ResultadoLaboratorialEstado.VALIDADO
        resultado.data_validacao = now
        resultado.validado_por = user
        resultado.save(update_fields=["estado", "data_validacao", "validado_por", "updated_at"])

        pedido = resultado.pedido_laboratorial
        if pedido.estado != PedidoLaboratorialEstado.CONCLUIDO:
            pedido.estado = PedidoLaboratorialEstado.CONCLUIDO
            pedido.data_conclusao = now
            pedido.save(update_fields=["estado", "data_conclusao", "updated_at"])
            pedido.exames.update(estado=PedidoLaboratorialEstado.CONCLUIDO, updated_at=now)
            if pedido.pedido_consulta_id:
                from apps.appointments.constants import PedidoEstado as ConsultaPedidoEstado

                pedido.pedido_consulta.estado = ConsultaPedidoEstado.CONCLUIDO
                pedido.pedido_consulta.save(update_fields=["estado", "updated_at"])

        consulta = pedido.consulta
        if resultado.conclusao:
            nota = f"\n[Lab {pedido.numero_pedido}] {resultado.conclusao}"
            consulta.clinical_notes = f"{consulta.clinical_notes}{nota}".strip()
            consulta.save(update_fields=["clinical_notes", "updated_at"])

        PatientHistoryService.record(
            patient=pedido.paciente,
            event_type=HistoryEventType.EXAME,
            title=f"Resultado laboratorial — {pedido.numero_pedido}",
            description=resultado.conclusao or "Resultado laboratorial validado.",
            user=user,
            source_module="laboratory",
            source_id=resultado.pk,
            metadata={"pedido_id": pedido.pk, "resultado_id": resultado.pk},
        )

        LaboratoryResultService._log(
            AuditAction.RESULTADO_VALIDADO,
            user,
            request,
            resultado,
            f"Resultado validado — pedido {pedido.numero_pedido}.",
        )

        event_bus.publish(
            EventNames.LABORATORY_RESULT_VALIDATED,
            {
                "resultado_id": resultado.pk,
                "pedido_id": pedido.pk,
                "consulta_id": pedido.consulta_id,
                "patient_id": pedido.paciente_id,
            },
        )

        from apps.laboratory.tasks import (
            actualizar_dashboard,
            actualizar_prontuario,
            notificar_medico,
        )

        actualizar_dashboard.delay()
        actualizar_prontuario.delay(resultado.pk)
        notificar_medico.delay(resultado.pk)

        LaboratoryCacheService.invalidate_all(patient_id=pedido.paciente_id, consulta_id=pedido.consulta_id)
        return resultado

    @staticmethod
    @transaction.atomic
    def publicar_resultado(resultado_id: int, user, request=None):
        LaboratoryResultService._ensure_laboratorio(user)
        resultado = (
            ResultadoLaboratorial.objects.select_for_update()
            .select_related("pedido_laboratorial")
            .get(pk=resultado_id)
        )
        if resultado.estado != ResultadoLaboratorialEstado.VALIDADO:
            raise ValueError("Apenas resultados validados podem ser publicados.")

        resultado.estado = ResultadoLaboratorialEstado.ENTREGUE
        resultado.data_publicacao = timezone.now()
        resultado.save(update_fields=["estado", "data_publicacao", "updated_at"])

        LaboratoryResultService._log(
            AuditAction.RESULTADO_PUBLICADO,
            user,
            request,
            resultado,
            f"Resultado publicado — pedido {resultado.pedido_laboratorial.numero_pedido}.",
        )

        event_bus.publish(
            EventNames.LABORATORY_RESULT_PUBLISHED,
            {
                "resultado_id": resultado.pk,
                "pedido_id": resultado.pedido_laboratorial_id,
            },
        )

        from apps.laboratory.tasks import publicar_resultado_async

        publicar_resultado_async.delay(resultado.pk)

        pedido = resultado.pedido_laboratorial
        LaboratoryCacheService.invalidate_all(patient_id=pedido.paciente_id, consulta_id=pedido.consulta_id)
        return resultado

    @staticmethod
    @transaction.atomic
    def anexar_documento(resultado_id: int, user, upload, *, descricao: str = "", request=None):
        LaboratoryResultService._ensure_laboratorio(user)
        from apps.files.models import StoredFile

        resultado = (
            ResultadoLaboratorial.objects.select_for_update()
            .select_related("pedido_laboratorial")
            .get(pk=resultado_id)
        )
        if not resultado.is_editavel:
            raise ValueError("Não é possível anexar ficheiros a um resultado validado.")

        mime = getattr(upload, "content_type", "")
        tipo = ALLOWED_ATTACHMENT_MIMES.get(mime)
        if not tipo:
            raise ValueError("Tipo de ficheiro não permitido. Use PDF, PNG, JPEG ou DOCX.")

        stored = StoredFile.objects.create(
            name=upload.name,
            file=upload,
            mime_type=mime,
            size=upload.size,
            uploaded_by=user,
        )
        anexo = AnexoResultado.objects.create(
            resultado=resultado,
            ficheiro=stored,
            tipo=tipo,
            descricao=descricao,
        )

        LaboratoryResultService._log(
            AuditAction.ANEXO_RESULTADO,
            user,
            request,
            resultado,
            f"Anexo {tipo} adicionado ao resultado.",
            metadata={"anexo_id": anexo.pk},
        )
        event_bus.publish(EventNames.FILE_UPLOADED, {"stored_file_id": stored.pk, "module": "laboratory"})
        return anexo

    @staticmethod
    def registar_download(resultado_id: int, user, request=None):
        resultado = ResultadoLaboratorial.objects.select_related("pedido_laboratorial").get(pk=resultado_id)
        LaboratoryResultService._log(
            AuditAction.RESULTADO_DOWNLOAD,
            user,
            request,
            resultado,
            f"Download do resultado — pedido {resultado.pedido_laboratorial.numero_pedido}.",
        )

    @staticmethod
    def get_dashboard_resultados() -> dict:
        from django.contrib.auth import get_user_model
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        User = get_user_model()
        today = timezone.localdate()

        pendentes = ResultadoLaboratorial.objects.filter(
            estado__in=[
                ResultadoLaboratorialEstado.EM_PROCESSAMENTO,
                ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
            ]
        ).count()
        validados = ResultadoLaboratorial.objects.filter(estado=ResultadoLaboratorialEstado.VALIDADO).count()
        entregues_hoje = ResultadoLaboratorial.objects.filter(
            estado=ResultadoLaboratorialEstado.ENTREGUE,
            data_publicacao__date=today,
        ).count()

        concluidos = ResultadoLaboratorial.objects.filter(
            data_validacao__isnull=False,
            data_resultado__isnull=False,
        ).order_by("-data_validacao")[:50]
        tempos = []
        for r in concluidos:
            delta = r.data_validacao - r.data_resultado
            tempos.append(delta.total_seconds() / 60)
        tempo_medio = round(sum(tempos) / len(tempos), 1) if tempos else 0

        por_tecnico = list(
            ResultadoLaboratorial.objects.filter(responsavel__isnull=False)
            .values("responsavel__first_name", "responsavel__last_name")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        por_dia = list(
            ResultadoLaboratorial.objects.filter(data_resultado__isnull=False)
            .annotate(dia=TruncDate("data_resultado"))
            .values("dia")
            .annotate(total=Count("id"))
            .order_by("-dia")[:7]
        )

        return {
            "resultados_pendentes": pendentes,
            "resultados_validados": validados,
            "resultados_entregues_hoje": entregues_hoje,
            "tempo_medio_validacao_minutos": tempo_medio,
            "exames_por_tecnico": [
                {
                    "tecnico": f"{r['responsavel__first_name']} {r['responsavel__last_name']}".strip(),
                    "total": r["total"],
                }
                for r in por_tecnico
            ],
            "exames_por_dia": [
                {"data": r["dia"].isoformat() if r["dia"] else None, "total": r["total"]} for r in por_dia
            ],
        }
