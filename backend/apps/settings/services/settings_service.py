"""Serviço principal de configurações."""

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.settings.constants import (
    DEFAULT_BILLING,
    DEFAULT_EMAIL,
    DEFAULT_FEATURE_FLAGS,
    DEFAULT_FILE_SETTINGS,
    DEFAULT_SECURITY,
    DEFAULT_SMS,
)
from apps.settings.models import (
    ConfiguracaoEmail,
    ConfiguracaoFaturacao,
    ConfiguracaoFicheiros,
    ConfiguracaoSeguranca,
    ConfiguracaoSms,
    FeatureFlag,
    PerfilClinica,
)
from apps.settings.services.cache_service import SettingsCacheService
from apps.settings.services.monitoring_service import MonitoringService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class SettingsService:
    @staticmethod
    def _log(action, user, request, resource_type, resource_id, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata=metadata or {},
        )

    @staticmethod
    def get_clinic_profile():
        cached = SettingsCacheService.get_clinic()
        if cached:
            return cached
        profile, _ = PerfilClinica.objects.get_or_create(pk=1, defaults={"nome": "SauVida Clínica"})
        data = {
            "id": profile.pk,
            "nome": profile.nome,
            "nif": profile.nif,
            "morada": profile.morada,
            "cidade": profile.cidade,
            "pais": profile.pais,
            "telefone": profile.telefone,
            "telemovel": profile.telemovel,
            "email": profile.email,
            "website": profile.website,
            "moeda": profile.moeda,
            "fuso_horario": profile.fuso_horario,
            "idioma": profile.idioma,
            "horario_funcionamento": profile.horario_funcionamento,
            "dias_uteis": profile.dias_uteis,
            "mensagem_rodape": profile.mensagem_rodape,
            "logotipo": profile.logotipo.url if profile.logotipo else None,
            "assinatura_digital": profile.assinatura_digital.url if profile.assinatura_digital else None,
        }
        SettingsCacheService.set_clinic(data)
        return data

    @staticmethod
    def update_clinic_profile(data: dict, user=None, request=None):
        profile, _ = PerfilClinica.objects.get_or_create(pk=1, defaults={"nome": "SauVida Clínica"})
        for field in (
            "nome", "nif", "morada", "cidade", "pais", "telefone", "telemovel",
            "email", "website", "moeda", "fuso_horario", "idioma",
            "horario_funcionamento", "dias_uteis", "mensagem_rodape",
        ):
            if field in data:
                setattr(profile, field, data[field])
        profile.save()
        SettingsCacheService.invalidate_all()
        SettingsService._log(
            AuditAction.SETTINGS_UPDATED,
            user, request, "clinic", profile.pk,
            "Perfil da clínica actualizado.",
        )
        event_bus.publish(EventNames.SETTINGS_UPDATED, {"area": "clinic"})
        return SettingsService.get_clinic_profile()

    @staticmethod
    def _get_singleton(model, defaults=None):
        obj, _ = model.objects.get_or_create(pk=1, defaults=defaults or {})
        return obj

    @staticmethod
    def get_billing_config():
        obj = SettingsService._get_singleton(
            ConfiguracaoFaturacao,
            {"metodos_pagamento": DEFAULT_BILLING["metodos_pagamento"]},
        )
        return {
            "iva_percentagem": float(obj.iva_percentagem),
            "moeda": obj.moeda,
            "serie_faturas": obj.serie_faturas,
            "serie_recibos": obj.serie_recibos,
            "serie_orcamentos": obj.serie_orcamentos,
            "desconto_maximo_percentagem": float(obj.desconto_maximo_percentagem),
            "metodos_pagamento": obj.metodos_pagamento,
        }

    @staticmethod
    def update_billing_config(data: dict, user=None, request=None):
        obj = SettingsService._get_singleton(ConfiguracaoFaturacao)
        for field in data:
            if hasattr(obj, field):
                setattr(obj, field, data[field])
        obj.save()
        SettingsCacheService.invalidate_all()
        SettingsService._log(
            AuditAction.SYSTEM_CONFIGURATION,
            user, request, "billing", 1,
            "Configuração de faturação actualizada.",
        )
        return SettingsService.get_billing_config()

    @staticmethod
    def get_email_config():
        obj = SettingsService._get_singleton(ConfiguracaoEmail)
        return {
            "host": obj.host,
            "port": obj.port,
            "use_ssl": obj.use_ssl,
            "use_tls": obj.use_tls,
            "username": obj.username,
            "from_email": obj.from_email,
            "password_configured": bool(obj.password),
        }

    @staticmethod
    def update_email_config(data: dict, user=None, request=None):
        obj = SettingsService._get_singleton(ConfiguracaoEmail, DEFAULT_EMAIL)
        for field in ("host", "port", "use_ssl", "use_tls", "username", "from_email"):
            if field in data:
                setattr(obj, field, data[field])
        if data.get("password"):
            obj.password = data["password"]
        obj.save()
        SettingsService._log(
            AuditAction.EMAIL_CONFIGURATION,
            user, request, "email", 1,
            "Configuração de e-mail actualizada.",
        )
        event_bus.publish(EventNames.SETTINGS_UPDATED, {"area": "email"})
        return SettingsService.get_email_config()

    @staticmethod
    def test_email_connection(user=None, request=None) -> dict:
        from apps.settings.tasks import send_test_email

        send_test_email.delay()
        return {"status": "stub", "message": "Teste de ligação SMTP agendado (stub)."}

    @staticmethod
    def get_security_config():
        obj = SettingsService._get_singleton(ConfiguracaoSeguranca)
        return {
            "sessao_maxima_minutos": obj.sessao_maxima_minutos,
            "password_min_length": obj.password_min_length,
            "password_require_upper": obj.password_require_upper,
            "password_require_number": obj.password_require_number,
            "password_require_special": obj.password_require_special,
            "password_expiry_days": obj.password_expiry_days,
            "password_history_count": obj.password_history_count,
            "max_login_attempts": obj.max_login_attempts,
            "lockout_minutes": obj.lockout_minutes,
            "two_factor_enabled": obj.two_factor_enabled,
        }

    @staticmethod
    def update_security_config(data: dict, user=None, request=None):
        obj = SettingsService._get_singleton(ConfiguracaoSeguranca)
        for field in data:
            if hasattr(obj, field) and field not in ("id", "created_at", "updated_at"):
                setattr(obj, field, data[field])
        obj.save()
        SettingsService._log(
            AuditAction.SECURITY_CONFIGURATION,
            user, request, "security", 1,
            "Configuração de segurança actualizada.",
        )
        return SettingsService.get_security_config()

    @staticmethod
    def get_sms_config():
        obj = SettingsService._get_singleton(ConfiguracaoSms, DEFAULT_SMS)
        return {
            "provider": obj.provider,
            "sender_id": obj.sender_id,
            "activo": obj.activo,
            "api_key_configured": bool(obj.api_key),
        }

    @staticmethod
    def update_sms_config(data: dict, user=None, request=None):
        obj = SettingsService._get_singleton(ConfiguracaoSms)
        for field in ("provider", "sender_id", "activo"):
            if field in data:
                setattr(obj, field, data[field])
        if data.get("api_key"):
            obj.api_key = data["api_key"]
        obj.save()
        return SettingsService.get_sms_config()

    @staticmethod
    def get_file_config():
        obj = SettingsService._get_singleton(ConfiguracaoFicheiros, DEFAULT_FILE_SETTINGS)
        return {
            "max_upload_mb": obj.max_upload_mb,
            "allowed_types": obj.allowed_types,
            "storage_backend": obj.storage_backend,
        }

    @staticmethod
    def update_file_config(data: dict, user=None, request=None):
        obj = SettingsService._get_singleton(ConfiguracaoFicheiros)
        for field in data:
            if hasattr(obj, field):
                setattr(obj, field, data[field])
        obj.save()
        return SettingsService.get_file_config()

    @staticmethod
    def ensure_feature_flags():
        for codigo, activo in DEFAULT_FEATURE_FLAGS.items():
            FeatureFlag.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nome": codigo.replace("_", " ").title(),
                    "activo": activo,
                },
            )

    @staticmethod
    def get_feature_flags():
        SettingsService.ensure_feature_flags()
        return list(
            FeatureFlag.objects.values("id", "codigo", "nome", "descricao", "activo")
        )

    @staticmethod
    def update_feature_flag(codigo: str, activo: bool, user=None, request=None):
        flag = FeatureFlag.objects.get(codigo=codigo)
        flag.activo = activo
        flag.save(update_fields=["activo", "updated_at"])
        SettingsService._log(
            AuditAction.FEATURE_FLAG_UPDATED,
            user, request, "feature_flag", codigo,
            f"Feature flag {codigo} = {activo}.",
            {"activo": activo},
        )
        event_bus.publish(EventNames.SYSTEM_UPDATED, {"feature_flag": codigo, "activo": activo})
        return flag

    @staticmethod
    def get_system_dashboard():
        cached = SettingsCacheService.get_system_dashboard()
        if cached:
            return cached
        from apps.settings.services.backup_service import BackupService

        data = {
            "monitorizacao": MonitoringService.get_system_status(),
            "backups_recentes": list(
                BackupService.listar_backups()[:5].values("id", "tipo", "estado", "created_at")
            ),
            "clinica": SettingsService.get_clinic_profile(),
            "feature_flags": SettingsService.get_feature_flags(),
        }
        SettingsCacheService.set_system_dashboard(data)
        event_bus.publish(EventNames.SYSTEM_UPDATED, {"dashboard": "system"})
        return data

    @staticmethod
    def get_setting(key: str, default=None):
        from apps.settings.models import ClinicSetting

        try:
            return ClinicSetting.objects.get(key=key, is_active=True).value
        except ClinicSetting.DoesNotExist:
            return default
