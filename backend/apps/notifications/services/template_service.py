"""Serviço de templates de notificação."""

import re

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.notifications.models import TemplateEmail, TemplateSMS

VARIAVEIS_PADRAO = ["nome", "consulta", "data", "hora", "clinica", "telefone"]
PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class TemplateService:
    @staticmethod
    def renderizar_texto(texto: str, contexto: dict | None = None) -> str:
        contexto = contexto or {}

        def substituir(match: re.Match) -> str:
            chave = match.group(1)
            return str(contexto.get(chave, match.group(0)))

        return PLACEHOLDER_RE.sub(substituir, texto)

    @staticmethod
    def preview_email(template: TemplateEmail, contexto: dict | None = None) -> dict:
        return {
            "assunto": TemplateService.renderizar_texto(template.assunto, contexto),
            "corpo": TemplateService.renderizar_texto(template.corpo, contexto),
        }

    @staticmethod
    def preview_sms(template: TemplateSMS, contexto: dict | None = None) -> dict:
        return {
            "mensagem": TemplateService.renderizar_texto(template.mensagem, contexto),
        }

    @staticmethod
    def criar_email(user, data: dict, request=None) -> TemplateEmail:
        template = TemplateEmail.objects.create(
            codigo=data["codigo"],
            nome=data["nome"],
            assunto=data["assunto"],
            corpo=data["corpo"],
            activo=data.get("activo", True),
            variaveis=data.get("variaveis", VARIAVEIS_PADRAO),
        )
        AuditService.log(
            action=AuditAction.TEMPLATE_CRIADO,
            user=user,
            request=request,
            description=f"Template e-mail '{template.codigo}' criado.",
            resource_type="template_email",
            resource_id=str(template.pk),
        )
        return template

    @staticmethod
    def actualizar_email(template: TemplateEmail, user, data: dict, request=None) -> TemplateEmail:
        for campo in ("nome", "assunto", "corpo", "activo", "variaveis"):
            if campo in data:
                setattr(template, campo, data[campo])
        template.save()
        AuditService.log(
            action=AuditAction.TEMPLATE_EDITADO,
            user=user,
            request=request,
            description=f"Template e-mail '{template.codigo}' editado.",
            resource_type="template_email",
            resource_id=str(template.pk),
        )
        return template

    @staticmethod
    def criar_sms(user, data: dict, request=None) -> TemplateSMS:
        template = TemplateSMS.objects.create(
            codigo=data["codigo"],
            nome=data["nome"],
            mensagem=data["mensagem"],
            activo=data.get("activo", True),
            variaveis=data.get("variaveis", VARIAVEIS_PADRAO),
        )
        AuditService.log(
            action=AuditAction.TEMPLATE_CRIADO,
            user=user,
            request=request,
            description=f"Template SMS '{template.codigo}' criado.",
            resource_type="template_sms",
            resource_id=str(template.pk),
        )
        return template

    @staticmethod
    def actualizar_sms(template: TemplateSMS, user, data: dict, request=None) -> TemplateSMS:
        for campo in ("nome", "mensagem", "activo", "variaveis"):
            if campo in data:
                setattr(template, campo, data[campo])
        template.save()
        AuditService.log(
            action=AuditAction.TEMPLATE_EDITADO,
            user=user,
            request=request,
            description=f"Template SMS '{template.codigo}' editado.",
            resource_type="template_sms",
            resource_id=str(template.pk),
        )
        return template
