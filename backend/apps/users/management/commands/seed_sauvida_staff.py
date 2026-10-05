"""
Cria ou actualiza utilizadores reais da clínica SauVida (piloto / produção).

Não usar em ambiente demo com seed_demo activo sem desactivar contas demo.

Ficheiro predefinido (gitignored):
  backend/data/private/sauvida_staff.json

Copiar de backend/data/clinic/sauvida_staff.example.json ou sauvida_staff.csv e ajustar.

Palavra-passe inicial:
  --password-file PATH   (primeira linha não vazia)
  ou variável SAUVIDA_STAFF_INITIAL_PASSWORD
  Piloto local: backend/data/private/pilot_initial_password.txt (gitignored; ex. Demo@2026!)
"""

from __future__ import annotations

import csv
import json
import os
import re
import unicodedata
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.authentication.models import UserRole
from apps.settings.models import MedicoPerfil

User = get_user_model()

ROLE_ALIASES = {
    "ADMIN": UserRole.ADMINISTRADOR,
    "ADMINISTRADOR": UserRole.ADMINISTRADOR,
    "RECECAO": UserRole.RECECIONISTA,
    "RECECIONISTA": UserRole.RECECIONISTA,
    "SECRETARIA": UserRole.RECECIONISTA,
    "MEDICO": UserRole.MEDICO,
    "ENFERMEIRO": UserRole.ENFERMEIRO,
    "PARTEIRA": UserRole.ENFERMEIRO,
    "LABORATORIO": UserRole.LABORATORIO,
    "LAB": UserRole.LABORATORIO,
    "DIRECTOR": UserRole.DIRECTOR,
}


def _slug_part(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", ".", normalized.lower().strip()).strip(".")
    return slug or "user"


def _default_email(first_name: str, last_name: str) -> str:
    local = f"{_slug_part(first_name)}.{_slug_part(last_name.split()[-1] if last_name else '')}"
    return f"{local}@sauvida.gw"


def _normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    if digits.startswith("245"):
        return f"+{digits}"
    if len(digits) == 9:
        return f"+245{digits}"
    return f"+{digits}" if raw.strip().startswith("+") else digits


def _load_staff_payload(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        rows: list[dict] = []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                first = (row.get("first_name") or "").strip()
                last = (row.get("last_name") or "").strip()
                if not first and not last:
                    continue
                entry = {
                    "first_name": first,
                    "last_name": last,
                    "phone": (row.get("phone") or "").strip(),
                    "role": (row.get("role") or "").strip(),
                    "position": (row.get("position") or "").strip(),
                    "email": (row.get("email") or "").strip(),
                }
                superuser = (row.get("is_superuser") or "").strip().lower()
                if superuser in ("1", "true", "yes", "sim"):
                    entry["is_superuser"] = True
                rows.append(entry)
        return rows

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise CommandError("O JSON deve ser uma lista de objectos utilizador.")
    return payload


def _load_password(options) -> str | None:
    path = options.get("password_file")
    if path:
        text = Path(path).read_text(encoding="utf-8").splitlines()
        for line in text:
            line = line.strip()
            if line and not line.startswith("#"):
                return line
        raise CommandError(f"Ficheiro de palavra-passe vazio ou só comentários: {path}")
    env = os.environ.get("SAUVIDA_STAFF_INITIAL_PASSWORD", "").strip()
    return env or None


class Command(BaseCommand):
    help = "Importa utilizadores SauVida a partir de JSON (piloto/produção)"

    def add_arguments(self, parser):
        default_json = Path(settings.BASE_DIR) / "data" / "private" / "sauvida_staff.json"
        default_csv = Path(settings.BASE_DIR) / "data" / "private" / "sauvida_staff.csv"
        default_file = default_csv if default_csv.is_file() else default_json
        parser.add_argument(
            "--file",
            type=str,
            default=str(default_file),
            help="JSON ou CSV com a equipa (predef.: private/sauvida_staff.csv ou .json)",
        )
        parser.add_argument(
            "--password-file",
            type=str,
            default="",
            help="Ficheiro com palavra-passe inicial (1.ª linha útil)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra acções sem gravar",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Actualiza telefone, cargo, perfil e palavra-passe se fornecida",
        )
        parser.add_argument(
            "--deactivate-demo-users",
            action="store_true",
            help="Desactiva contas *@sauvida.gw de seed_demo (excepto as do JSON)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(
                f"Ficheiro não encontrado: {path}\n"
                "Copie backend/data/clinic/sauvida_staff.csv (ou .example.json) para "
                "backend/data/private/sauvida_staff.csv"
            )

        payload = _load_staff_payload(path)
        if not payload:
            raise CommandError("Nenhum utilizador no ficheiro (preenche pelo menos uma linha com nome).")

        password = _load_password(options)
        dry_run = options["dry_run"]
        update = options["update_existing"]

        if not dry_run and not password and not update:
            raise CommandError(
                "Forneça palavra-passe inicial (--password-file ou "
                "SAUVIDA_STAFF_INITIAL_PASSWORD) ou use --update-existing sem alterar passwords."
            )

        keep_emails = set()
        created = updated = skipped = 0

        for entry in payload:
            email = (entry.get("email") or "").strip().lower()
            first_name = (entry.get("first_name") or "").strip()
            last_name = (entry.get("last_name") or "").strip()
            if not email:
                if not first_name or not last_name:
                    raise CommandError(f"Entrada inválida (falta email ou nome): {entry!r}")
                email = _default_email(first_name, last_name)

            role_key = (entry.get("role") or "").strip().upper()
            role = ROLE_ALIASES.get(role_key)
            if not role:
                raise CommandError(f"Perfil desconhecido «{role_key}» para {email}")

            phone = _normalize_phone(entry.get("phone") or "")
            position = (entry.get("position") or "").strip()
            is_admin = role == UserRole.ADMINISTRADOR
            medico_perfil = bool(entry.get("medico_perfil", role == UserRole.MEDICO))

            keep_emails.add(email)

            if dry_run:
                action = "criar" if not User.objects.filter(email=email).exists() else "actualizar"
                self.stdout.write(f"  [dry-run] {action}: {email} ({role}) {first_name} {last_name}")
                continue

            existing = User.objects.filter(email=email).first()
            if existing:
                if not update:
                    skipped += 1
                    self.stdout.write(f"  · já existe (omitido): {email}")
                else:
                    existing.first_name = first_name or existing.first_name
                    existing.last_name = last_name or existing.last_name
                    existing.role = role
                    existing.phone = phone or existing.phone
                    existing.position = position or existing.position
                    existing.is_active = True
                    if is_admin:
                        existing.is_staff = True
                    if password:
                        existing.set_password(password)
                    existing.save()
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"  ↻ actualizado: {email}"))
                user = existing
            else:
                if not password:
                    raise CommandError(
                        f"Criar {email} requer palavra-passe inicial (novos utilizadores)."
                    )
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    phone=phone,
                    position=position,
                    is_staff=is_admin,
                    is_superuser=bool(entry.get("is_superuser", is_admin)),
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ criado: {email} ({role})"))

            if user and medico_perfil and role == UserRole.MEDICO:
                MedicoPerfil.objects.get_or_create(
                    utilizador=user,
                    defaults={"activo": True, "disponivel_marcacao": True},
                )

        if options["deactivate_demo_users"] and not dry_run:
            demo_qs = User.objects.filter(email__endswith="@sauvida.gw").exclude(email__in=keep_emails)
            count = demo_qs.update(is_active=False)
            if count:
                self.stdout.write(self.style.WARNING(f"  · contas demo desactivadas: {count}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído: {created} criados, {updated} actualizados, {skipped} omitidos."
            )
        )
