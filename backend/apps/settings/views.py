"""Views do módulo de configurações."""

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.settings.models import (
    BackupRegisto,
    Consultorio,
    Departamento,
    EspecialidadeMedica,
    Feriado,
    HorarioFuncionamento,
    MedicoPerfil,
    TipoConsulta,
    TipoExameLaboratorio,
)
from apps.settings.permissions import (
    BACKUP_MAP,
    CONSULTATION_TYPE_MAP,
    DEPARTMENT_MAP,
    HOLIDAY_MAP,
    LAB_EXAM_MAP,
    ROOM_MAP,
    SPECIALTY_MAP,
    WORKING_HOURS_MAP,
    SettingsPermissionMixin,
)
from apps.settings.serializers import (
    BackupRegistoSerializer,
    ConsultorioSerializer,
    DepartamentoSerializer,
    EspecialidadeMedicaSerializer,
    FeriadoSerializer,
    HorarioFuncionamentoSerializer,
    TipoConsultaSerializer,
    TipoExameLaboratorioSerializer,
    MedicoPerfilSerializer,
)
from apps.settings.services.backup_service import BackupService
from apps.settings.services.settings_service import SettingsService
from apps.users.permissions import HasModulePermission
from core.pagination import StandardPagination
from core.responses import error_response, success_response


class SettingsApiMixin:
    permission_classes = [HasModulePermission]
    view_permission = "settings.view"
    edit_permission = "settings.edit"

    def initial(self, request, *args, **kwargs):
        if request.method in ("PATCH", "PUT", "POST", "DELETE"):
            self.required_permission = self.edit_permission
        else:
            self.required_permission = self.view_permission
        super().initial(request, *args, **kwargs)


class SettingsModelViewSet(SettingsPermissionMixin, viewsets.ModelViewSet):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Registo criado.", status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Registo actualizado.")

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response(message="Registo eliminado.", status=status.HTTP_200_OK)


class EspecialidadeViewSet(SettingsModelViewSet):
    queryset = EspecialidadeMedica.objects.all()
    serializer_class = EspecialidadeMedicaSerializer
    permission_map = SPECIALTY_MAP


class DepartamentoViewSet(SettingsModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_map = DEPARTMENT_MAP


class ConsultorioViewSet(SettingsModelViewSet):
    queryset = Consultorio.objects.select_related("departamento")
    serializer_class = ConsultorioSerializer
    permission_map = ROOM_MAP


class HorarioViewSet(SettingsModelViewSet):
    queryset = HorarioFuncionamento.objects.all()
    serializer_class = HorarioFuncionamentoSerializer
    permission_map = WORKING_HOURS_MAP


class FeriadoViewSet(SettingsModelViewSet):
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_map = HOLIDAY_MAP


class TipoConsultaViewSet(SettingsModelViewSet):
    queryset = TipoConsulta.objects.all()
    serializer_class = TipoConsultaSerializer
    permission_map = CONSULTATION_TYPE_MAP


class TipoExameViewSet(SettingsModelViewSet):
    queryset = TipoExameLaboratorio.objects.select_related("servico")
    serializer_class = TipoExameLaboratorioSerializer
    permission_map = LAB_EXAM_MAP


class MedicoPerfilViewSet(SettingsModelViewSet):
    queryset = MedicoPerfil.objects.select_related(
        "utilizador", "especialidade", "departamento", "servico_consulta"
    )
    serializer_class = MedicoPerfilSerializer
    permission_map = SPECIALTY_MAP


class BackupViewSet(SettingsPermissionMixin, viewsets.ModelViewSet):
    queryset = BackupRegisto.objects.all()
    serializer_class = BackupRegistoSerializer
    permission_map = BACKUP_MAP
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        tipo = request.data.get("tipo", BackupRegisto.TIPO_MANUAL)
        backup = BackupService.criar_backup(tipo, user=request.user, request=request)
        return success_response(
            data=BackupRegistoSerializer(backup).data,
            message="Backup criado com sucesso.",
            status=201,
        )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        backup = BackupService.restaurar_backup(int(pk), user=request.user, request=request)
        return success_response(
            data=BackupRegistoSerializer(backup).data,
            message="Restauro de backup iniciado.",
        )


class ClinicSettingsView(SettingsApiMixin, APIView):
    @extend_schema(tags=["Configurações — Clínica"])
    def get(self, request):
        return success_response(data=SettingsService.get_clinic_profile())

    @extend_schema(tags=["Configurações — Clínica"])
    def patch(self, request):
        data = SettingsService.update_clinic_profile(request.data, user=request.user, request=request)
        return success_response(data=data, message="Dados da clínica actualizados.")


class BillingSettingsView(SettingsApiMixin, APIView):
    @extend_schema(tags=["Configurações — Faturação"])
    def get(self, request):
        return success_response(data=SettingsService.get_billing_config())

    @extend_schema(tags=["Configurações — Faturação"])
    def patch(self, request):
        data = SettingsService.update_billing_config(request.data, user=request.user, request=request)
        return success_response(data=data, message="Configuração de faturação actualizada.")


class EmailSettingsView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.email"

    @extend_schema(tags=["Configurações — E-mail"])
    def get(self, request):
        return success_response(data=SettingsService.get_email_config())

    @extend_schema(tags=["Configurações — E-mail"])
    def patch(self, request):
        data = SettingsService.update_email_config(request.data, user=request.user, request=request)
        return success_response(data=data, message="Configuração de e-mail actualizada.")


class EmailTestView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.email"

    @extend_schema(tags=["Configurações — E-mail"])
    def post(self, request):
        result = SettingsService.test_email_connection(user=request.user, request=request)
        return success_response(data=result, message="Teste de ligação SMTP agendado.")


class SecuritySettingsView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.security"

    @extend_schema(tags=["Configurações — Segurança"])
    def get(self, request):
        return success_response(data=SettingsService.get_security_config())

    @extend_schema(tags=["Configurações — Segurança"])
    def patch(self, request):
        data = SettingsService.update_security_config(request.data, user=request.user, request=request)
        return success_response(data=data, message="Configuração de segurança actualizada.")


class SmsSettingsView(SettingsApiMixin, APIView):

    @extend_schema(tags=["Configurações — SMS"])
    def get(self, request):
        return success_response(data=SettingsService.get_sms_config())

    @extend_schema(tags=["Configurações — SMS"])
    def patch(self, request):
        data = SettingsService.update_sms_config(request.data, user=request.user, request=request)
        return success_response(data=data, message="Configuração SMS actualizada.")


class FileSettingsView(SettingsApiMixin, APIView):

    @extend_schema(tags=["Configurações — Ficheiros"])
    def get(self, request):
        return success_response(data=SettingsService.get_file_config())

    @extend_schema(tags=["Configurações — Ficheiros"])
    def patch(self, request):
        data = SettingsService.update_file_config(request.data, user=request.user, request=request)
        return success_response(data=data, message="Configuração de ficheiros actualizada.")


class FeatureFlagsView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.featureflags"

    @extend_schema(tags=["Configurações — Feature Flags"])
    def get(self, request):
        return success_response(data=SettingsService.get_feature_flags())

    @extend_schema(tags=["Configurações — Feature Flags"])
    def patch(self, request):
        codigo = request.data.get("codigo")
        activo = request.data.get("activo")
        if codigo is None or activo is None:
            return error_response("Campos codigo e activo são obrigatórios.")
        flag = SettingsService.update_feature_flag(codigo, bool(activo), user=request.user, request=request)
        from apps.settings.serializers import FeatureFlagSerializer
        return success_response(data=FeatureFlagSerializer(flag).data, message="Feature flag actualizada.")


class MonitoringView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.system"

    @extend_schema(tags=["Configurações — Monitorização"])
    def get(self, request):
        from apps.settings.services.monitoring_service import MonitoringService
        return success_response(data=MonitoringService.get_system_status())
