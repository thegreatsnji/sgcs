from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.audit_logs.services import AuditService
from apps.users.services.user_service import UserService
from core.security.login_guard import LoginGuardService

from .models import UserRole

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer JWT que aceita e-mail em vez de nome de utilizador."""

    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        token["full_name"] = user.get_full_name()
        return token

    def validate(self, attrs):
        email = attrs.get("email", "")
        if email and not LoginGuardService.is_allowed(email):
            raise serializers.ValidationError(
                "Demasiadas tentativas de login. Tente novamente mais tarde."
            )
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            if email:
                LoginGuardService.record_failure(email)
            raise
        if email:
            LoginGuardService.clear(email)
        user = self.user
        request = self.context.get("request")
        AuditService.log_login(user, request)
        refresh = data.get("refresh", "")
        refresh_jti = ""
        if refresh:
            try:
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh_jti = str(RefreshToken(refresh).get("jti", ""))
            except Exception:
                refresh_jti = ""
        UserService.create_session(user, request, refresh_jti=refresh_jti)
        UserService.touch_activity(user)
        return data


class UserSerializer(serializers.ModelSerializer):
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
            "birth_date",
            "position",
            "photo_url",
            "role",
            "is_active",
            "date_joined",
            "last_login",
            "last_activity",
        )
        read_only_fields = (
            "id",
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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As palavras-passe não coincidem."}
            )
        return attrs

    def validate_role(self, value):
        if value == UserRole.ADMINISTRADOR:
            raise serializers.ValidationError(
                "Não é permitido registar administradores por esta via."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
