from django.apps import AppConfig


class ClinicSettingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.settings"
    label = "clinic_settings"
    verbose_name = "Configurações da Clínica"
