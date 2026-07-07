"""Gera scaffolds das apps Django do SGCS."""

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "backend"

APPS = [
    ("users", "Utilizadores"),
    ("patients", "Pacientes"),
    ("appointments", "Consultas"),
    ("reception", "Receção"),
    ("doctors", "Médicos"),
    ("laboratory", "Laboratório"),
    ("billing", "Faturação"),
    ("finance", "Finanças"),
    ("reports", "Relatórios"),
    ("dashboard", "Dashboard"),
    ("notifications", "Notificações"),
    ("audit_logs", "Registos de Auditoria"),
    ("common", "Comum"),
]

EXTRA_APPS = {"notifications", "audit_logs"}


def class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def create_app(name: str, verbose: str) -> None:
    app_dir = BASE / "apps" / name
    (app_dir / "migrations").mkdir(parents=True, exist_ok=True)

    config_class = f"{class_name(name)}Config"
    apps_content = (
        "from django.apps import AppConfig\n\n\n"
        f"class {config_class}(AppConfig):\n"
        '    default_auto_field = "django.db.models.BigAutoField"\n'
        f'    name = "apps.{name}"\n'
        f'    label = "{name}"\n'
        f'    verbose_name = "{verbose}"\n'
    )

    if name in EXTRA_APPS:
        apps_content += (
            "\n    def ready(self) -> None:\n"
            "        # Importar signals na Sprint 3+\n"
            "        # from . import signals  # noqa: F401\n"
            "        pass\n"
        )

    files = {
        "__init__.py": "",
        "apps.py": apps_content,
        "models.py": f'"""Modelos do módulo {verbose}."""\n\n# Estrutura preparada para implementação nas próximas sprints.\n',
        "serializers.py": f'"""Serializers do módulo {verbose}."""\n\n# Estrutura preparada para implementação nas próximas sprints.\n',
        "views.py": f'"""Views do módulo {verbose}."""\n\n# Estrutura preparada para implementação nas próximas sprints.\n',
        "urls.py": (
            f'"""URLs do módulo {verbose}."""\n\n'
            "from django.urls import path\n\n"
            f'app_name = "{name}"\n\n'
            "urlpatterns = []\n"
        ),
        "admin.py": (
            f'"""Admin do módulo {verbose}."""\n\n'
            "from django.contrib import admin\n\n"
            "# Registos de modelos serão adicionados nas próximas sprints.\n"
        ),
        "migrations/__init__.py": "",
    }

    if name in EXTRA_APPS:
        files["services.py"] = (
            f'"""Serviços do módulo {verbose}."""\n\n'
            "# Estrutura preparada para implementação nas próximas sprints.\n"
        )
        files["signals.py"] = (
            f'"""Signals do módulo {verbose}."""\n\n'
            "# Estrutura preparada para implementação nas próximas sprints.\n"
        )

    for rel, content in files.items():
        path = app_dir / rel
        if not path.exists():
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    for app_name, app_verbose in APPS:
        create_app(app_name, app_verbose)
    print("Apps criadas com sucesso.")
