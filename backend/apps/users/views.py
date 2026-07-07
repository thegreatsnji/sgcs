"""Views do módulo de utilizadores."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.users.filters import UserFilter
from apps.users.models import ModulePermission, Role, UserGroup, UserSession
from apps.users.permissions import HasModulePermission
from apps.users.serializers import (
    ModulePermissionSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserGroupSerializer,
    UserListSerializer,
    UserSessionSerializer,
    UserUpdateSerializer,
)
from apps.users.services.export_service import ExportService
from apps.users.services.rbac_service import RBACService
from apps.users.services.user_service import UserService
from core.pagination import StandardPagination
from core.responses import error_response, success_response

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filterset_class = UserFilter
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["date_joined", "last_login", "first_name", "email"]
    ordering = ["first_name"]

    def get_queryset(self):
        return User.objects.all().order_by("first_name", "last_name")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def get_permissions(self):
        permission_map = {
            "list": "users.view",
            "retrieve": "users.view",
            "create": "users.create",
            "update": "users.edit",
            "partial_update": "users.edit",
            "destroy": "users.delete",
            "activate": "users.edit",
            "deactivate": "users.edit",
            "export": "users.export",
        }
        codename = permission_map.get(self.action, "users.view")
        return [HasModulePermission()]

    def get_required_permission(self):
        permission_map = {
            "list": "users.view",
            "retrieve": "users.view",
            "create": "users.create",
            "update": "users.edit",
            "partial_update": "users.edit",
            "destroy": "users.delete",
            "activate": "users.edit",
            "deactivate": "users.edit",
            "export": "users.export",
        }
        return permission_map.get(self.action, "users.view")

    @property
    def required_permission(self):
        return self.get_required_permission()

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
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        AuditService.log(
            action=AuditAction.USER_CREATE,
            user=request.user,
            request=request,
            description=f"Utilizador {user.email} criado.",
            resource_type="user",
            resource_id=user.pk,
        )
        return success_response(
            data=UserDetailSerializer(user, context={"request": request}).data,
            message="Utilizador criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not RBACService.can_manage_role(request.user, instance.role):
            return error_response("Sem permissão para editar este utilizador.", status=403)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]
            user.save(update_fields=["photo"])
        AuditService.log(
            action=AuditAction.USER_UPDATE,
            user=request.user,
            request=request,
            description=f"Utilizador {user.email} atualizado.",
            resource_type="user",
            resource_id=user.pk,
        )
        return success_response(
            data=UserDetailSerializer(user, context={"request": request}).data,
            message="Utilizador atualizado com sucesso.",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            UserService.soft_delete_user(request.user, instance, request)
        except ValueError as exc:
            return error_response(str(exc), status=400)
        return success_response(message="Utilizador eliminado com sucesso.")

    @extend_schema(request=None, responses={200: dict})
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        instance = self.get_object()
        UserService.activate_user(request.user, instance, request)
        return success_response(message="Utilizador ativado com sucesso.")

    @extend_schema(request=None, responses={200: dict})
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        instance = self.get_object()
        try:
            UserService.deactivate_user(request.user, instance, request)
        except ValueError as exc:
            return error_response(str(exc), status=400)
        return success_response(message="Utilizador desativado com sucesso.")

    @extend_schema(request=None, responses={200: dict})
    @action(detail=False, methods=["get"])
    def export(self, request):
        try:
            ExportService.export_users(request.query_params.get("format", "csv"), self.get_queryset())
        except NotImplementedError as exc:
            return success_response(
                data={"formats": list(ExportService.SUPPORTED_FORMATS), "ready": False},
                message=str(exc),
            )
        return success_response(message="Exportação concluída.")


class ProfileView(APIView):
    def get(self, request):
        serializer = UserDetailSerializer(request.user, context={"request": request})
        permissions = sorted(RBACService.get_user_permissions(request.user))
        return success_response(
            data={
                **serializer.data,
                "permissions": permissions,
            }
        )

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]
            user.save(update_fields=["photo"])
        AuditService.log(
            action=AuditAction.PROFILE_UPDATE,
            user=request.user,
            request=request,
            description="Perfil atualizado.",
            resource_type="user",
            resource_id=user.pk,
        )
        return success_response(
            data=UserDetailSerializer(user, context={"request": request}).data,
            message="Perfil atualizado com sucesso.",
        )


class PasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        AuditService.log(
            action=AuditAction.PASSWORD_CHANGE,
            user=request.user,
            request=request,
            description="Palavra-passe alterada.",
            resource_type="user",
            resource_id=request.user.pk,
        )
        return success_response(message="Palavra-passe alterada com sucesso.")


class MySessionsView(generics.ListAPIView):
    serializer_class = UserSessionSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user).order_by("-last_activity")

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
            }
        )


class MyAccessHistoryView(generics.ListAPIView):
    pagination_class = StandardPagination

    def get_queryset(self):
        from apps.audit_logs.models import AuditLog

        return AuditLog.objects.filter(
            user=self.request.user,
            action__in=[AuditAction.LOGIN, AuditAction.LOGOUT],
        ).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        from apps.audit_logs.serializers import AuditLogSerializer

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = AuditLogSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            }
        )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related("permissions").all()
    serializer_class = RoleSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self):
        if self.action in ("list", "retrieve"):
            return "users.view"
        return "users.admin"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(data=paginated.data)

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        AuditService.log(
            action=AuditAction.PERMISSION_CHANGE,
            user=request.user,
            request=request,
            description=f"Perfil {role.name} criado.",
            resource_type="role",
            resource_id=role.pk,
        )
        return success_response(
            data=RoleSerializer(role).data,
            message="Perfil criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system and request.data.get("slug") != instance.slug:
            return error_response("Não é possível alterar perfis do sistema.", status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        AuditService.log(
            action=AuditAction.PERMISSION_CHANGE,
            user=request.user,
            request=request,
            description=f"Perfil {role.name} atualizado.",
            resource_type="role",
            resource_id=role.pk,
        )
        return success_response(data=RoleSerializer(role).data, message="Perfil atualizado com sucesso.")


class PermissionListView(generics.ListAPIView):
    queryset = ModulePermission.objects.all()
    serializer_class = ModulePermissionSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self):
        return "users.view"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(data=paginated.data)


class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = UserGroup.objects.prefetch_related("permissions", "members").all()
    serializer_class = UserGroupSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self):
        if self.action in ("list", "retrieve"):
            return "users.view"
        return "users.admin"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(data=paginated.data)

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        AuditService.log(
            action=AuditAction.GROUP_CREATE,
            user=request.user,
            request=request,
            description=f"Grupo {group.name} criado.",
            resource_type="group",
            resource_id=group.pk,
        )
        return success_response(
            data=UserGroupSerializer(group).data,
            message="Grupo criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        AuditService.log(
            action=AuditAction.GROUP_UPDATE,
            user=request.user,
            request=request,
            description=f"Grupo {group.name} atualizado.",
            resource_type="group",
            resource_id=group.pk,
        )
        return success_response(data=UserGroupSerializer(group).data, message="Grupo atualizado com sucesso.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name
        instance.delete()
        AuditService.log(
            action=AuditAction.GROUP_DELETE,
            user=request.user,
            request=request,
            description=f"Grupo {name} eliminado.",
            resource_type="group",
            resource_id=kwargs.get("pk"),
        )
        return success_response(message="Grupo eliminado com sucesso.")
