"""Serializers do módulo de utilizadores."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import ModulePermission, Role, UserGroup, UserSession
from apps.users.validators import validate_password_change, validate_role_assignment

User = get_user_model()


class ModulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulePermission
        fields = ("id", "module", "action", "codename", "name", "description")


class RoleSerializer(serializers.ModelSerializer):
    permissions = ModulePermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=ModulePermission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="permissions",
    )
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_system",
            "permissions",
            "permission_ids",
            "permission_count",
        )
        read_only_fields = ("is_system",)

    def get_permission_count(self, obj) -> int:
        return obj.permissions.count()


class UserGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=ModulePermission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="permissions",
    )
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="members",
    )
    permissions = ModulePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = UserGroup
        fields = (
            "id",
            "name",
            "description",
            "is_active",
            "permissions",
            "permission_ids",
            "member_ids",
            "members_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_members_count(self, obj) -> int:
        return obj.members.count()


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "gender",
            "role",
            "position",
            "photo_url",
            "is_active",
            "date_joined",
            "last_login",
            "last_activity",
        )

    def get_photo_url(self, obj) -> str | None:
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class UserDetailSerializer(UserListSerializer):
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ("birth_date",)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "gender",
            "birth_date",
            "position",
            "role",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As palavras-passe não coincidem."}
            )
        validate_password(attrs["password"])
        request = self.context.get("request")
        if request:
            validate_role_assignment(request.user, attrs.get("role", ""))
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "gender",
            "birth_date",
            "position",
            "role",
            "is_active",
        )

    def validate_role(self, value):
        request = self.context.get("request")
        if request:
            validate_role_assignment(request.user, value)
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "gender",
            "birth_date",
            "position",
        )


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "As palavras-passe não coincidem."}
            )
        validate_password(attrs["new_password"])
        user = self.context["request"].user
        try:
            validate_password_change(user, attrs["old_password"], attrs["new_password"])
        except Exception as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = (
            "id",
            "ip_address",
            "user_agent",
            "is_active",
            "created_at",
            "last_activity",
            "logged_out_at",
        )
