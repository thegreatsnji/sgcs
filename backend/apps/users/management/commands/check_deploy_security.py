"""Executa verificações Django de deploy (segurança SGCS)."""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Verifica SECRET_KEY, ALLOWED_HOSTS, CORS/CSRF, SSL (python manage.py check --deploy)"

    def handle(self, *args, **options):
        call_command("check", deploy=True)
