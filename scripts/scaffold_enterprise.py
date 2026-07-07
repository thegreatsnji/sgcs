"""Gera apps enterprise da Sprint 3.5."""

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "backend"

ENTERPRISE_APPS = [
    {
        "name": "settings",
        "label": "clinic_settings",
        "verbose": "Configurações da Clínica",
        "config_class": "ClinicSettingsConfig",
        "with_services": True,
    },
    {
        "name": "files",
        "label": "files",
        "verbose": "Ficheiros e Documentos",
        "config_class": "FilesConfig",
        "with_services": True,
    },
    {
        "name": "analytics",
        "label": "analytics",
        "verbose": "Analytics",
        "config_class": "AnalyticsConfig",
        "with_services": True,
    },
]


def create_enterprise_app(spec: dict) -> None:
    name = spec["name"]
    app_dir = BASE / "apps" / name
    (app_dir / "migrations").mkdir(parents=True, exist_ok=True)
    (app_dir / "services").mkdir(parents=True, exist_ok=True)
    (app_dir / "tests").mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": "",
        "apps.py": (
            "from django.apps import AppConfig\n\n\n"
            f"class {spec['config_class']}(AppConfig):\n"
            '    default_auto_field = "django.db.models.BigAutoField"\n'
            f'    name = "apps.{name}"\n'
            f'    label = "{spec["label"]}"\n'
            f'    verbose_name = "{spec["verbose"]}"\n'
        ),
        "models.py": f'"""Modelos do módulo {spec["verbose"]}."""\n\n# Estrutura preparada para implementação futura.\n',
        "serializers.py": f'"""Serializers do módulo {spec["verbose"]}."""\n\n# Estrutura preparada para implementação futura.\n',
        "views.py": f'"""Views do módulo {spec["verbose"]}."""\n\n# Estrutura preparada para implementação futura.\n',
        "urls.py": (
            f'"""URLs do módulo {spec["verbose"]}."""\n\n'
            "from django.urls import path\n\n"
            f'app_name = "{name}"\n\n'
            "urlpatterns = []\n"
        ),
        "admin.py": (
            f'"""Admin do módulo {spec["verbose"]}."""\n\n'
            "from django.contrib import admin\n\n"
            "# Registos de modelos serão adicionados em sprints futuras.\n"
        ),
        "services/__init__.py": "",
        "services/service.py": (
            f'"""Serviços do módulo {spec["verbose"]}."""\n\n'
            "# Estrutura preparada para implementação futura.\n"
        ),
        "migrations/__init__.py": "",
        "tests/__init__.py": "",
        "tests/test_app.py": (
            '"""Testes base do módulo."""\n\n'
            "def test_placeholder():\n"
            "    assert True\n"
        ),
    }

    if name == "settings":
        files["models.py"] = (
            '"""Modelos de configuração da clínica."""\n\n'
            "from django.db import models\n\n\n"
            "class ClinicSetting(models.Model):\n"
            '    key = models.CharField("Chave", max_length=100, unique=True)\n'
            '    value = models.JSONField("Valor", default=dict)\n'
            '    description = models.TextField("Descrição", blank=True)\n'
            '    is_active = models.BooleanField("Ativo", default=True)\n'
            '    updated_at = models.DateTimeField("Atualizado em", auto_now=True)\n\n'
            "    class Meta:\n"
            '        verbose_name = "Configuração"\n'
            '        verbose_name_plural = "Configurações"\n'
            '        ordering = ["key"]\n\n'
            "    def __str__(self) -> str:\n"
            "        return self.key\n"
        )
        files["services/service.py"] = (
            '"""Serviços de configuração da clínica."""\n\n\n'
            "class ClinicSettingsService:\n"
            "    @staticmethod\n"
            "    def get_setting(key: str, default=None):\n"
            "        from apps.settings.models import ClinicSetting\n\n"
            "        try:\n"
            "            return ClinicSetting.objects.get(key=key, is_active=True).value\n"
            "        except ClinicSetting.DoesNotExist:\n"
            "            return default\n"
        )
    elif name == "files":
        files["models.py"] = (
            '"""Modelos de ficheiros e documentos."""\n\n'
            "from django.conf import settings\n"
            "from django.db import models\n\n\n"
            "class StoredFile(models.Model):\n"
            '    name = models.CharField("Nome", max_length=255)\n'
            '    file = models.FileField("Ficheiro", upload_to="documents/")\n'
            '    mime_type = models.CharField("Tipo MIME", max_length=100, blank=True)\n'
            '    size = models.PositiveIntegerField("Tamanho (bytes)", default=0)\n'
            "    uploaded_by = models.ForeignKey(\n"
            "        settings.AUTH_USER_MODEL,\n"
            "        on_delete=models.SET_NULL,\n"
            "        null=True,\n"
            "        blank=True,\n"
            "        related_name=\"uploaded_files\",\n"
            '        verbose_name="Carregado por",\n'
            "    )\n"
            '    created_at = models.DateTimeField("Criado em", auto_now_add=True)\n\n'
            "    class Meta:\n"
            '        verbose_name = "Ficheiro"\n'
            '        verbose_name_plural = "Ficheiros"\n'
            '        ordering = ["-created_at"]\n'
        )
        files["services/service.py"] = (
            '"""Serviços de gestão de ficheiros."""\n\n\n'
            "class FileStorageService:\n"
            "    @staticmethod\n"
            '    def build_upload_path(category: str, filename: str) -> str:\n'
            '        return f"{category}/{filename}"\n'
        )
    elif name == "analytics":
        files["models.py"] = (
            '"""Modelos de analytics."""\n\n'
            "from django.db import models\n\n\n"
            "class AnalyticsEvent(models.Model):\n"
            '    event_name = models.CharField("Evento", max_length=100)\n'
            '    payload = models.JSONField("Dados", default=dict, blank=True)\n'
            '    recorded_at = models.DateTimeField("Registado em", auto_now_add=True)\n\n'
            "    class Meta:\n"
            '        verbose_name = "Evento de analytics"\n'
            '        verbose_name_plural = "Eventos de analytics"\n'
            '        ordering = ["-recorded_at"]\n'
        )
        files["services/service.py"] = (
            '"""Serviços de analytics."""\n\n\n'
            "class AnalyticsService:\n"
            "    @staticmethod\n"
            "    def record_event(event_name: str, payload: dict | None = None):\n"
            "        from apps.analytics.models import AnalyticsEvent\n\n"
            "        return AnalyticsEvent.objects.create(event_name=event_name, payload=payload or {})\n"
        )

    for rel, content in files.items():
        path = app_dir / rel
        if not path.exists():
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    for app in ENTERPRISE_APPS:
        create_enterprise_app(app)
    print("Apps enterprise criadas.")
