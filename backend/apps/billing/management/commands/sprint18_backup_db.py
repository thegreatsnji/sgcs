"""Backup PostgreSQL para Sprint 18 (pré-importação)."""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria backup SQL em backups/pre_sprint18/ antes de importações"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="",
            help="Directório de destino (predefinição: <repo>/backups/pre_sprint18)",
        )

    def handle(self, *args, **options):
        db = settings.DATABASES.get("default", {})
        engine = db.get("ENGINE", "")
        if "postgresql" not in engine:
            raise CommandError(f"Motor não suportado para backup automático: {engine}")

        root = Path(settings.BASE_DIR).parent
        out_dir = Path(options["output_dir"]) if options["output_dir"] else root / "backups" / "pre_sprint18"
        out_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"sgcs_pre_import_catalogo_{stamp}.sql"
        out_path = out_dir / filename

        env = os.environ.copy()
        if db.get("PASSWORD"):
            env["PGPASSWORD"] = str(db["PASSWORD"])

        cmd = [
            "pg_dump",
            "-h",
            str(db.get("HOST") or "localhost"),
            "-p",
            str(db.get("PORT") or "5432"),
            "-U",
            str(db.get("USER") or "postgres"),
            "-d",
            str(db.get("NAME") or "sgcs"),
            "-f",
            str(out_path),
            "--no-owner",
            "--no-acl",
        ]

        try:
            subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise CommandError(
                "pg_dump não encontrado. Instale as ferramentas PostgreSQL client."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"pg_dump falhou: {exc.stderr or exc.stdout}") from exc

        if not out_path.is_file() or out_path.stat().st_size == 0:
            raise CommandError("Backup não foi criado ou está vazio.")

        digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
        meta_path = out_path.with_suffix(".meta.txt")
        meta_path.write_text(
            f"file={out_path.name}\n"
            f"size_bytes={out_path.stat().st_size}\n"
            f"sha256={digest}\n"
            f"created={datetime.now().isoformat()}\n",
            encoding="utf-8",
        )

        self.stdout.write(self.style.SUCCESS(f"Backup criado: {out_path}"))
        self.stdout.write(f"Tamanho: {out_path.stat().st_size} bytes")
        self.stdout.write(f"SHA256: {digest}")
        self.stdout.write(f"Meta: {meta_path}")
