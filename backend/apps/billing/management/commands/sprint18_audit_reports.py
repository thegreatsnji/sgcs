"""Relatórios Sprint 18 — materialização e médicos."""

from __future__ import annotations

import csv
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.authentication.models import UserRole
from apps.billing.models import Servico
from apps.settings.models import MedicoPerfil

DATA_ROOT = Path(settings.BASE_DIR) / "data"
DOCS_ROOT = Path(settings.BASE_DIR).parent / "docs"


class Command(BaseCommand):
    help = "Gera docs/SPRINT18_MATERIALIZACAO_SERVICOS.md e SPRINT18_MEDICOS_CONFIGURACAO.md"

    def handle(self, *args, **options):
        self._materializacao()
        self._medicos()
        self.stdout.write(self.style.SUCCESS("Relatórios Sprint 18 gerados."))

    def _materializacao(self):
        catalog_path = DATA_ROOT / "catalogo_servicos_sauvida.csv"
        lines = [
            "# Materialização de serviços — Sprint 18",
            "",
            "| Código | Serviço | Existe na BD | Preço confirmado | Acção prevista |",
            "|---|---|---|---|---|",
        ]
        with catalog_path.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                codigo = row["codigo"].strip()
                nome = row["nome"].strip()
                svc = Servico.objects.filter(codigo=codigo).first()
                existe = "Sim" if svc else "Não"
                preco_conf = "Sim" if svc and svc.preco_confirmado else "Não"
                if not svc:
                    accao = "CRIAR"
                elif not svc.preco_confirmado:
                    accao = "MANTER (preço pendente)"
                else:
                    accao = "MANTER"
                lines.append(f"| {codigo} | {nome} | {existe} | {preco_conf} | {accao} |")
        (DOCS_ROOT / "SPRINT18_MATERIALIZACAO_SERVICOS.md").write_text("\n".join(lines), encoding="utf-8")

    def _medicos(self):
        User = get_user_model()
        medicos = User.objects.filter(role=UserRole.MEDICO, is_active=True).order_by("last_name")
        lines = [
            "# Configuração de médicos — Sprint 18",
            "",
            "| Médico | Perfil | Especialidade | Departamento | Serviço | Horário | Estado |",
            "|---|---|---|---|---|---|---|",
        ]
        for user in medicos:
            perfil = MedicoPerfil.objects.filter(utilizador=user).first()
            if not perfil:
                lines.append(
                    f"| {user.get_full_name()} | Não | — | — | — | — | PENDENTE_DE_CONFIGURACAO |"
                )
                continue
            horario = "Configurado" if perfil.horario_configurado else "Pendente"
            servico = perfil.servico_consulta.nome if perfil.servico_consulta_id else "—"
            esp = perfil.especialidade.nome if perfil.especialidade_id else "—"
            dept = perfil.departamento.nome if perfil.departamento_id else "—"
            completo = all(
                [
                    perfil.especialidade_id,
                    perfil.departamento_id,
                    perfil.servico_consulta_id,
                    perfil.horario_configurado,
                    perfil.activo,
                ]
            )
            estado = "CONFIGURADO" if completo and perfil.disponivel_marcacao else "PENDENTE_DE_CONFIGURACAO"
            lines.append(
                f"| {user.get_full_name()} | Sim | {esp} | {dept} | {servico} | {horario} | {estado} |"
            )
        (DOCS_ROOT / "SPRINT18_MEDICOS_CONFIGURACAO.md").write_text("\n".join(lines), encoding="utf-8")
