import os

from django.core.management.base import BaseCommand

from apps.authentication.models import User, UserRole


class Command(BaseCommand):
    help = "Cria um superutilizador para desenvolvimento"

    def handle(self, *args, **options):
        email = os.getenv("SUPERUSER_EMAIL", "admin@sauvida.ao")
        password = os.getenv("SUPERUSER_PASSWORD", "Admin@12345")
        first_name = os.getenv("SUPERUSER_FIRST_NAME", "Administrador")
        last_name = os.getenv("SUPERUSER_LAST_NAME", "SGCS")

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Superutilizador já existe: {email}"))
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMINISTRADOR,
        )
        self.stdout.write(self.style.SUCCESS(f"Superutilizador criado: {email}"))
