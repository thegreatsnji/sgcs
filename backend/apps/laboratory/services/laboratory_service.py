"""Serviços do módulo de laboratório."""

from django.db import transaction
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.laboratory.constants import (
    COLLECTION_QUEUE_STATUSES,
    DEFAULT_EXAM_CATEGORY,
    PENDING_STATUSES,
    PedidoLaboratorialEstado,
)
from apps.laboratory.models import ExameLaboratorial, PedidoLaboratorial
from apps.laboratory.services.number_service import LaboratoryNumberService
from apps.laboratory.validators import validate_pedido_editavel, validate_transicao


class LaboratoryService:
    @staticmethod
    def _log(action, user, request, pedido, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="laboratory_order",
            resource_id=str(pedido.pk),
            metadata=metadata
            or {
                "numero_pedido": pedido.numero_pedido,
                "patient_id": pedido.paciente_id,
            },
        )

    @staticmethod
    def _sync_exames_estado(pedido: PedidoLaboratorial, estado: str) -> None:
        pedido.exames.update(estado=estado, updated_at=timezone.now())

    @staticmethod
    @transaction.atomic
    def criar_de_pedido_consulta(pedido_consulta, user=None) -> PedidoLaboratorial:
        """Cria pedido laboratorial a partir de um PedidoLaboratorio da consulta."""
        if hasattr(pedido_consulta, "pedido_laboratorial"):
            return pedido_consulta.pedido_laboratorial

        consulta = pedido_consulta.consulta
        pedido = PedidoLaboratorial.objects.create(
            numero_pedido=LaboratoryNumberService.generate(),
            consulta=consulta,
            paciente=consulta.patient,
            medico=consulta.doctor,
            pedido_consulta=pedido_consulta,
            prioridade=pedido_consulta.prioridade,
            observacoes=pedido_consulta.observacoes,
            estado=PedidoLaboratorialEstado.PENDENTE,
            registado_por=user or pedido_consulta.solicitado_por,
        )
        ExameLaboratorial.objects.create(
            pedido=pedido,
            nome_exame=pedido_consulta.tipo_exame,
            categoria=DEFAULT_EXAM_CATEGORY,
            estado=PedidoLaboratorialEstado.PENDENTE,
        )
        return pedido

    @staticmethod
    def listar_pendentes():
        return (
            PedidoLaboratorial.objects.filter(estado__in=PENDING_STATUSES)
            .select_related("paciente", "medico", "consulta")
            .prefetch_related("exames")
            .order_by("-prioridade", "data_pedido")
        )

    @staticmethod
    def listar_do_dia(*, day=None):
        target = day or timezone.localdate()
        return (
            PedidoLaboratorial.objects.filter(data_pedido__date=target)
            .select_related("paciente", "medico", "consulta")
            .prefetch_related("exames")
            .order_by("-data_pedido")
        )

    @staticmethod
    def fila_colheitas():
        return (
            PedidoLaboratorial.objects.filter(estado__in=COLLECTION_QUEUE_STATUSES)
            .select_related("paciente", "medico")
            .order_by("data_pedido")
        )

    @staticmethod
    @transaction.atomic
    def receber_pedido(pedido_id: int, user, request=None) -> PedidoLaboratorial:
        pedido = PedidoLaboratorial.objects.select_for_update().get(pk=pedido_id)
        validate_transicao(
            pedido.estado,
            {PedidoLaboratorialEstado.PENDENTE},
            "receber o pedido",
        )
        now = timezone.now()
        pedido.estado = PedidoLaboratorialEstado.RECEBIDO
        pedido.data_rececao = now
        pedido.save(update_fields=["estado", "data_rececao", "updated_at"])
        LaboratoryService._sync_exames_estado(pedido, PedidoLaboratorialEstado.RECEBIDO)

        LaboratoryService._log(
            AuditAction.PEDIDO_LABORATORIO_RECEBIDO,
            user,
            request,
            pedido,
            f"Pedido {pedido.numero_pedido} recebido no laboratório.",
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def registar_colheita(pedido_id: int, user, request=None) -> PedidoLaboratorial:
        pedido = PedidoLaboratorial.objects.select_for_update().get(pk=pedido_id)
        validate_transicao(
            pedido.estado,
            {PedidoLaboratorialEstado.RECEBIDO, PedidoLaboratorialEstado.AGUARDANDO_COLHEITA},
            "registar colheita",
        )
        now = timezone.now()
        pedido.estado = PedidoLaboratorialEstado.AGUARDANDO_COLHEITA
        pedido.data_colheita = now
        pedido.save(update_fields=["estado", "data_colheita", "updated_at"])
        LaboratoryService._sync_exames_estado(pedido, PedidoLaboratorialEstado.AGUARDANDO_COLHEITA)

        LaboratoryService._log(
            AuditAction.COLHEITA_REALIZADA,
            user,
            request,
            pedido,
            f"Colheita registada — pedido {pedido.numero_pedido}.",
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def iniciar_processamento(pedido_id: int, user, request=None) -> PedidoLaboratorial:
        pedido = PedidoLaboratorial.objects.select_for_update().get(pk=pedido_id)
        validate_transicao(
            pedido.estado,
            {
                PedidoLaboratorialEstado.RECEBIDO,
                PedidoLaboratorialEstado.AGUARDANDO_COLHEITA,
            },
            "iniciar processamento",
        )
        pedido.estado = PedidoLaboratorialEstado.EM_PROCESSAMENTO
        pedido.save(update_fields=["estado", "updated_at"])
        LaboratoryService._sync_exames_estado(pedido, PedidoLaboratorialEstado.EM_PROCESSAMENTO)

        LaboratoryService._log(
            AuditAction.EXAME_INICIADO,
            user,
            request,
            pedido,
            f"Processamento iniciado — pedido {pedido.numero_pedido}.",
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def concluir_exame(pedido_id: int, user, request=None) -> PedidoLaboratorial:
        pedido = PedidoLaboratorial.objects.select_for_update().get(pk=pedido_id)
        validate_transicao(
            pedido.estado,
            {PedidoLaboratorialEstado.EM_PROCESSAMENTO},
            "concluir exame",
        )
        now = timezone.now()
        pedido.estado = PedidoLaboratorialEstado.CONCLUIDO
        pedido.data_conclusao = now
        pedido.save(update_fields=["estado", "data_conclusao", "updated_at"])
        LaboratoryService._sync_exames_estado(pedido, PedidoLaboratorialEstado.CONCLUIDO)

        if pedido.pedido_consulta_id:
            from apps.appointments.constants import PedidoEstado as ConsultaPedidoEstado

            pedido_consulta = pedido.pedido_consulta
            pedido_consulta.estado = ConsultaPedidoEstado.CONCLUIDO
            pedido_consulta.save(update_fields=["estado", "updated_at"])

        LaboratoryService._log(
            AuditAction.EXAME_CONCLUIDO,
            user,
            request,
            pedido,
            f"Exame concluído — pedido {pedido.numero_pedido}.",
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def actualizar_pedido(
        pedido_id: int,
        user,
        *,
        observacoes: str | None = None,
        prioridade: str | None = None,
        request=None,
    ) -> PedidoLaboratorial:
        pedido = PedidoLaboratorial.objects.select_for_update().get(pk=pedido_id)
        validate_pedido_editavel(pedido.estado)

        update_fields = ["updated_at"]
        if observacoes is not None:
            pedido.observacoes = observacoes
            update_fields.append("observacoes")
        if prioridade is not None:
            pedido.prioridade = prioridade
            update_fields.append("prioridade")
        pedido.save(update_fields=update_fields)
        return pedido

    @staticmethod
    def get_dashboard_summary() -> dict:
        from apps.laboratory.services.laboratory_result_service import LaboratoryResultService

        today = timezone.localdate()
        qs_hoje = PedidoLaboratorial.objects.filter(data_pedido__date=today)
        pendentes = PedidoLaboratorial.objects.filter(estado__in=PENDING_STATUSES).count()
        em_processamento = PedidoLaboratorial.objects.filter(
            estado=PedidoLaboratorialEstado.EM_PROCESSAMENTO
        ).count()
        concluidos_hoje = qs_hoje.filter(estado=PedidoLaboratorialEstado.CONCLUIDO).count()

        concluidos = PedidoLaboratorial.objects.filter(
            estado=PedidoLaboratorialEstado.CONCLUIDO,
            data_rececao__isnull=False,
            data_conclusao__isnull=False,
        ).order_by("-data_conclusao")[:50]

        tempos = []
        for p in concluidos:
            delta = p.data_conclusao - p.data_rececao
            tempos.append(delta.total_seconds() / 60)
        tempo_medio = round(sum(tempos) / len(tempos), 1) if tempos else 0

        return {
            "indicadores": {
                "pedidos_pendentes": pendentes,
                "em_processamento": em_processamento,
                "concluidos_hoje": concluidos_hoje,
                "tempo_medio_minutos": tempo_medio,
            },
            "cards": {
                "pending": pendentes,
                "in_progress": em_processamento,
                "completed_today": concluidos_hoje,
                "avg_time_minutes": tempo_medio,
            },
            "resultados": LaboratoryResultService.get_dashboard_resultados(),
        }
