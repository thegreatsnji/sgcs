# Script de criação de superutilizador para desenvolvimento
# Uso: python scripts/create_superuser.py

import os
import sys
from pathlib import Path

import django

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django.setup()

from apps.authentication.models import User, UserRole  # noqa: E402

EMAIL = os.getenv("SUPERUSER_EMAIL", "admin@sauvida.ao")
PASSWORD = os.getenv("SUPERUSER_PASSWORD", "Admin@12345")
FIRST_NAME = os.getenv("SUPERUSER_FIRST_NAME", "Administrador")
LAST_NAME = os.getenv("SUPERUSER_LAST_NAME", "SGCS")


def main():
    if User.objects.filter(email=EMAIL).exists():
        print(f"Superutilizador já existe: {EMAIL}")
        return

    User.objects.create_superuser(
        email=EMAIL,
        password=PASSWORD,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        role=UserRole.ADMINISTRADOR,
    )
    print(f"Superutilizador criado: {EMAIL}")


if __name__ == "__main__":
    main()
