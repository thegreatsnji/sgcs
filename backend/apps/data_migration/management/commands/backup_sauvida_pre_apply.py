"""Backup PostgreSQL obrigatório antes de --apply da migração histórica."""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Dump PostgreSQL em backups/pre_sauvida_hist/ com tamanho e SHA256."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", type=str, default="")

    def handle(self, *args, **options):
        db = settings.DATABASES.get("default", {})
        root = Path(settings.BASE_DIR).parent
        out_dir = Path(options["output_dir"]) if options["output_dir"] else root / "backups" / "pre_sauvida_hist"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"sgcs_pre_sauvida_hist_{stamp}.sql"

        docker_cmd = [
            "docker",
            "exec",
            "sgcs-db",
            "pg_dump",
            "-U",
            str(db.get("USER") or "sgcs"),
            str(db.get("NAME") or "sgcs"),
        ]
        try:
            completed = subprocess.run(docker_cmd, check=True, capture_output=True)
            out_path.write_bytes(completed.stdout)
        except (FileNotFoundError, subprocess.CalledProcessError):
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
                    "Não foi possível executar pg_dump (nem via docker exec sgcs-db). "
                    "Ver docs/MIGRACAO_HISTORICA_BACKUP.md."
                ) from exc
            except subprocess.CalledProcessError as exc:
                raise CommandError(f"pg_dump falhou: {exc.stderr or exc.stdout}") from exc

        if not out_path.is_file() or out_path.stat().st_size == 0:
            raise CommandError("Backup não foi criado ou está vazio. --apply recusado.")

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
