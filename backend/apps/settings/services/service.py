"""Serviços de configuração da clínica."""

from apps.settings.services.settings_service import SettingsService


class ClinicSettingsService:
    @staticmethod
    def get_setting(key: str, default=None):
        return SettingsService.get_setting(key, default)
