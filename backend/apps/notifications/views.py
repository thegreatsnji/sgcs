"""Views do módulo Notificações."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.authentication.models import User
from apps.notifications.models import HistoricoEmail, HistoricoSMS, Notificacao, TemplateEmail, TemplateSMS
from apps.notifications.permissions import (
    EMAIL_MAP,
    NOTIFICATION_MAP,
    PREFERENCE_MAP,
    SMS_MAP,
    TEMPLATE_MAP,
    NotificationsPermissionMixin,
)
from apps.notifications.serializers import (
    EmailTestSerializer,
    HistoricoEmailSerializer,
    HistoricoSMSSerializer,
    NotificacaoCreateSerializer,
    NotificacaoSerializer,
    PreferenciaNotificacaoSerializer,
    SMSTestSerializer,
    TemplateEmailSerializer,
    TemplatePreviewSerializer,
    TemplateSMSSerializer,
)
from apps.notifications.services.email_service import EmailService
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.services.preference_service import NotificationPreferenceService
from apps.notifications.services.sms_service import SMSService
from apps.notifications.services.template_service import TemplateService
from core.pagination import StandardPagination
from core.responses import success_response


class NotificationsBaseViewSet(NotificationsPermissionMixin, viewsets.ModelViewSet):
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Registos obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Registo actualizado.")


@extend_schema_view(
    list=extend_schema(tags=["Notificações"]),
    retrieve=extend_schema(tags=["Notificações"]),
    create=extend_schema(tags=["Notificações"]),
    partial_update=extend_schema(tags=["Notificações"]),
    destroy=extend_schema(tags=["Notificações"]),
)
class NotificacaoViewSet(NotificationsBaseViewSet):
    serializer_class = NotificacaoSerializer
    permission_map = NOTIFICATION_MAP

    def get_queryset(self):
        user = self.request.user
        qs = Notificacao.objects.all().order_by("-created_at")
        if user.role != "ADMINISTRADOR" and not user.is_superuser:
            qs = qs.filter(utilizador=user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = NotificacaoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        utilizador = None
        if data.get("utilizador_id"):
            utilizador = User.objects.filter(pk=data["utilizador_id"]).first()
        elif request.user.is_authenticated:
            utilizador = request.user
        notificacao = NotificationService.criar(
            titulo=data["titulo"],
            mensagem=data["mensagem"],
            utilizador=utilizador,
            tipo=data.get("tipo", "INFORMATIVA"),
            canal=data.get("canal", "INTERNO"),
            destinatario_email=data.get("destinatario_email", ""),
            destinatario_telefone=data.get("destinatario_telefone", ""),
            criador=request.user,
            request=request,
        )
        return success_response(
            data=NotificacaoSerializer(notificacao).data if notificacao else {},
            message="Notificação criada.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notificacao = NotificationService.marcar_lida(int(pk), request.user, request=request)
        return success_response(data=NotificacaoSerializer(notificacao).data, message="Notificação lida.")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        notificacao = NotificationService.arquivar(int(pk), request.user)
        return success_response(data=NotificacaoSerializer(notificacao).data, message="Notificação arquivada.")

    @action(detail=False, methods=["get"])
    def unread(self, request):
        return success_response(
            data={
                "contador": NotificationService.contador_nao_lidas(request.user),
                "notificacoes": NotificationService.listar_nao_lidas(request.user),
            }
        )

    @action(detail=False, methods=["get"])
    def history(self, request):
        return success_response(data={"historico": NotificationService.historico(request.user)})


@extend_schema_view(
    list=extend_schema(tags=["Notificações — E-mail"]),
    test=extend_schema(tags=["Notificações — E-mail"]),
    history=extend_schema(tags=["Notificações — E-mail"]),
)
class EmailViewSet(NotificationsPermissionMixin, viewsets.ViewSet):
    permission_map = EMAIL_MAP
    default_permission = "notifications.send"

    def get_permissions(self):
        from apps.users.permissions import HasModulePermission

        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        action = getattr(self, "action", "")
        return self.permission_map.get(action, self.default_permission)

    @action(detail=False, methods=["post"])
    def test(self, request):
        serializer = EmailTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        historico = EmailService.enviar_teste(
            serializer.validated_data["destinatario"],
            request.user,
            request=request,
        )
        return success_response(data=HistoricoEmailSerializer(historico).data, message="E-mail de teste enviado.")

    @action(detail=False, methods=["get"])
    def history(self, request):
        qs = HistoricoEmail.objects.all().order_by("-enviado_em")[:100]
        return success_response(data=HistoricoEmailSerializer(qs, many=True).data)


@extend_schema_view(
    list=extend_schema(tags=["Notificações — SMS"]),
    test=extend_schema(tags=["Notificações — SMS"]),
    history=extend_schema(tags=["Notificações — SMS"]),
)
class SMSViewSet(NotificationsPermissionMixin, viewsets.ViewSet):
    permission_map = SMS_MAP
    default_permission = "notifications.send"

    def get_permissions(self):
        from apps.users.permissions import HasModulePermission

        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        action = getattr(self, "action", "")
        return self.permission_map.get(action, self.default_permission)

    @action(detail=False, methods=["post"])
    def test(self, request):
        serializer = SMSTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        historico = SMSService.enviar_teste(
            serializer.validated_data["telefone"],
            request.user,
            request=request,
        )
        return success_response(data=HistoricoSMSSerializer(historico).data, message="SMS de teste enviado.")

    @action(detail=False, methods=["get"])
    def history(self, request):
        qs = HistoricoSMS.objects.all().order_by("-enviado_em")[:100]
        return success_response(data=HistoricoSMSSerializer(qs, many=True).data)


@extend_schema_view(
    list=extend_schema(tags=["Notificações — Templates"]),
    retrieve=extend_schema(tags=["Notificações — Templates"]),
    create=extend_schema(tags=["Notificações — Templates"]),
    partial_update=extend_schema(tags=["Notificações — Templates"]),
    destroy=extend_schema(tags=["Notificações — Templates"]),
)
class TemplateEmailViewSet(NotificationsBaseViewSet):
    queryset = TemplateEmail.objects.all()
    serializer_class = TemplateEmailSerializer
    permission_map = TEMPLATE_MAP

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.criar_email(request.user, serializer.validated_data, request=request)
        return success_response(
            data=TemplateEmailSerializer(template).data,
            message="Template criado.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = self.get_serializer(template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.actualizar_email(template, request.user, serializer.validated_data, request=request)
        return success_response(data=TemplateEmailSerializer(template).data, message="Template actualizado.")

    @action(detail=True, methods=["post"])
    def preview(self, request, pk=None):
        template = self.get_object()
        serializer = TemplatePreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(data=TemplateService.preview_email(template, serializer.validated_data.get("contexto")))


@extend_schema_view(
    list=extend_schema(tags=["Notificações — Templates"]),
    retrieve=extend_schema(tags=["Notificações — Templates"]),
    create=extend_schema(tags=["Notificações — Templates"]),
    partial_update=extend_schema(tags=["Notificações — Templates"]),
    destroy=extend_schema(tags=["Notificações — Templates"]),
)
class TemplateSMSViewSet(NotificationsBaseViewSet):
    queryset = TemplateSMS.objects.all()
    serializer_class = TemplateSMSSerializer
    permission_map = TEMPLATE_MAP

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.criar_sms(request.user, serializer.validated_data, request=request)
        return success_response(
            data=TemplateSMSSerializer(template).data,
            message="Template criado.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = self.get_serializer(template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        template = TemplateService.actualizar_sms(template, request.user, serializer.validated_data, request=request)
        return success_response(data=TemplateSMSSerializer(template).data, message="Template actualizado.")

    @action(detail=True, methods=["post"])
    def preview(self, request, pk=None):
        template = self.get_object()
        serializer = TemplatePreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(data=TemplateService.preview_sms(template, serializer.validated_data.get("contexto")))


class PreferenciaView(APIView):
    required_permission = "notifications.settings"

    def get_permissions(self):
        from apps.users.permissions import HasModulePermission

        return [HasModulePermission()]

    @extend_schema(tags=["Notificações — Preferências"])
    def get(self, request):
        pref = NotificationPreferenceService.obter_ou_criar(request.user)
        return success_response(data=PreferenciaNotificacaoSerializer(pref).data)

    @extend_schema(tags=["Notificações — Preferências"])
    def patch(self, request):
        pref = NotificationPreferenceService.actualizar(request.user, request.data, request=request)
        return success_response(data=PreferenciaNotificacaoSerializer(pref).data, message="Preferências actualizadas.")
