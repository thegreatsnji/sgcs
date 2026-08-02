"""Backup da BD antes do apply do Catálogo SauVida V1."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria backup PostgreSQL em backups/pre_catalogo_sauvida_v1/"

    def handle(self, *args, **options):
        out_dir = Path(settings.BASE_DIR).parent / "backups" / "pre_catalogo_sauvida_v1"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        out_file = out_dir / f"sgcs_pre_catalogo_sauvida_v1_{stamp}.sql"

        db = settings.DATABASES["default"]
        env = {**subprocess.os.environ}
        if db.get("PASSWORD"):
            env["PGPASSWORD"] = db["PASSWORD"]

        cmd = [
            "pg_dump",
            "-h",
            db.get("HOST", "localhost"),
            "-p",
            str(db.get("PORT", 5432)),
            "-U",
            db.get("USER", "postgres"),
            "-d",
            db.get("NAME", "sgcs"),
            "-f",
            str(out_file),
        ]
        try:
            subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise CommandError(
                "pg_dump não encontrado. Use Docker ou instale PostgreSQL client tools."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise CommandError(exc.stderr or str(exc)) from exc

        digest = hashlib.sha256(out_file.read_bytes()).hexdigest()
        meta = out_dir / f"sgcs_pre_catalogo_sauvida_v1_{stamp}.sha256"
        meta.write_text(f"{digest}  {out_file.name}\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Backup: {out_file} ({out_file.stat().st_size} bytes)"))
        self.stdout.write(f"SHA256: {digest}")
