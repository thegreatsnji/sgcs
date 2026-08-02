"""Comando para inicializar permissões e perfis RBAC."""

from django.core.management.base import BaseCommand

from apps.authentication.models import UserRole
from apps.users.models import ModulePermission, PermissionAction, Role, SystemModule

MODULES = [
    SystemModule.PATIENTS,
    SystemModule.APPOINTMENTS,
    SystemModule.RECEPTION,
    SystemModule.LABORATORY,
    SystemModule.BILLING,
    SystemModule.FINANCE,
    SystemModule.REPORTS,
    SystemModule.DASHBOARD,
    SystemModule.USERS,
    SystemModule.SETTINGS,
    SystemModule.DOCTORS,
    SystemModule.NOTIFICATIONS,
]

ACTIONS = [
    PermissionAction.VIEW,
    PermissionAction.CREATE,
    PermissionAction.EDIT,
    PermissionAction.DELETE,
    PermissionAction.EXPORT,
    PermissionAction.PRINT,
    PermissionAction.ADMIN,
]

APPOINTMENTS_WORKFLOW_ACTIONS = [
    PermissionAction.CONFIRM,
    PermissionAction.START,
    PermissionAction.FINISH,
    PermissionAction.CANCEL,
]

APPOINTMENTS_CLINICAL_ACTIONS = [
    PermissionAction.CLINICAL,
    PermissionAction.DIAGNOSIS,
    PermissionAction.REQUEST_LAB,
    PermissionAction.REQUEST_IMAGING,
    PermissionAction.FOLLOWUP,
]

LABORATORY_WORKFLOW_ACTIONS = [
    PermissionAction.RECEIVE,
    PermissionAction.COLLECT,
    PermissionAction.PROCESS,
    PermissionAction.FINISH,
]

LABORATORY_RESULTS_ACTIONS = [
    PermissionAction.RESULTS_VIEW,
    PermissionAction.RESULTS_CREATE,
    PermissionAction.RESULTS_EDIT,
    PermissionAction.RESULTS_VALIDATE,
    PermissionAction.RESULTS_PUBLISH,
    PermissionAction.RESULTS_DOWNLOAD,
]

BILLING_EXTRA_ACTIONS = [
    PermissionAction.PAYMENT,
    PermissionAction.RECEIPT,
    PermissionAction.QUOTE,
]

FINANCE_EXTRA_ACTIONS = [
    PermissionAction.CASH,
    PermissionAction.EXPENSE,
    PermissionAction.REPORT,
    PermissionAction.FIN_DASHBOARD,
]

REPORTS_EXTRA_ACTIONS = [
    PermissionAction.FIN_DASHBOARD,
    PermissionAction.STATISTICS,
]

SETTINGS_EXTRA_ACTIONS = [
    PermissionAction.SECURITY,
    PermissionAction.BACKUP,
    PermissionAction.SYSTEM,
    PermissionAction.EMAIL,
    PermissionAction.FEATUREFLAGS,
]

DOCTORS_EXTRA_ACTIONS = [
    PermissionAction.PRESCRIPTION,
    PermissionAction.TREATMENT,
    PermissionAction.EVOLUTION,
    PermissionAction.DISCHARGE,
    PermissionAction.FOLLOWUP,
]

NOTIFICATIONS_EXTRA_ACTIONS = [
    PermissionAction.SEND,
    PermissionAction.TEMPLATE,
    PermissionAction.SETTINGS,
    PermissionAction.HISTORY,
]

DEFAULT_ROLE_PERMISSIONS = {
    UserRole.ADMINISTRADOR: "__all__",
    UserRole.RECECIONISTA: [
        "patients.view", "patients.create", "patients.edit",
        "appointments.view", "appointments.create", "appointments.edit",
        "appointments.confirm", "appointments.cancel",
        "reception.view", "reception.create", "reception.edit",
        # Faturação operacional na receção (sem delete/export nem módulo finance)
        "billing.view",
        "billing.create",
        "billing.edit",
        "billing.payment",
        "billing.receipt",
        "billing.print",
        "dashboard.view",
        "notifications.view",
    ],
    UserRole.MEDICO: [
        "patients.view", "patients.edit",
        "appointments.view", "appointments.create", "appointments.edit",
        "appointments.start", "appointments.finish",
        "appointments.clinical", "appointments.diagnosis",
        "appointments.request_lab", "appointments.request_imaging",
        "appointments.followup",
        "laboratory.results.view", "laboratory.results.download",
        "billing.view",
        "dashboard.view",
        "doctors.prescription", "doctors.treatment", "doctors.evolution",
        "doctors.discharge", "doctors.followup",
        "notifications.view", "notifications.settings", "notifications.history",
    ],
    UserRole.ENFERMEIRO: [
        "patients.view",
        "appointments.view", "appointments.edit",
        "dashboard.view",
    ],
    UserRole.LABORATORIO: [
        "patients.view",
        "laboratory.view", "laboratory.edit",
        "laboratory.receive", "laboratory.collect",
        "laboratory.process", "laboratory.finish",
        "laboratory.results.view", "laboratory.results.create",
        "laboratory.results.edit", "laboratory.results.validate",
        "laboratory.results.publish", "laboratory.results.download",
        "dashboard.view",
        "notifications.view",
    ],
    UserRole.FINANCEIRO: [
        "patients.view",
        "billing.view", "billing.create", "billing.edit", "billing.delete",
        "billing.export", "billing.payment", "billing.receipt", "billing.quote",
        "finance.view", "finance.create", "finance.edit", "finance.delete",
        "finance.cash", "finance.expense", "finance.report", "finance.dashboard",
        "reports.view", "reports.export", "reports.dashboard", "reports.statistics",
        "settings.view", "settings.edit", "settings.security", "settings.backup",
        "settings.system", "settings.email", "settings.featureflags",
        "dashboard.view",
        "notifications.view",
    ],
    UserRole.DIRECTOR: [
        "patients.view", "patients.create", "patients.edit", "patients.export", "patients.print",
        "appointments.view", "appointments.create", "appointments.edit", "appointments.confirm",
        "appointments.start", "appointments.finish", "appointments.cancel",
        "appointments.clinical", "appointments.diagnosis",
        "appointments.request_lab", "appointments.request_imaging", "appointments.followup",
        "doctors.view", "doctors.prescription", "doctors.treatment", "doctors.evolution",
        "doctors.discharge", "doctors.followup",
        "laboratory.view", "laboratory.results.view", "laboratory.results.download",
        "billing.view", "billing.create", "billing.edit", "billing.delete",
        "billing.export", "billing.payment", "billing.receipt", "billing.quote",
        "finance.view", "finance.create", "finance.edit", "finance.delete",
        "finance.cash", "finance.expense", "finance.report", "finance.dashboard",
        "reports.view", "reports.export", "reports.dashboard", "reports.statistics",
        "dashboard.view",
        "notifications.view", "notifications.send", "notifications.template",
        "notifications.settings", "notifications.history",
    ],
}

DEFAULT_GROUPS = [
    ("Receção Principal", "Equipa principal de receção", UserRole.RECECIONISTA),
    ("Laboratório Central", "Equipa do laboratório central", UserRole.LABORATORIO),
    ("Direção", "Direção clínica", UserRole.DIRECTOR),
]


class Command(BaseCommand):
    help = "Inicializa permissões, perfis e grupos padrão do RBAC"

    def handle(self, *args, **options):
        permissions = {}
        for module in MODULES:
            module_actions = list(ACTIONS)
            if module == SystemModule.APPOINTMENTS:
                module_actions.extend(APPOINTMENTS_WORKFLOW_ACTIONS)
                module_actions.extend(APPOINTMENTS_CLINICAL_ACTIONS)
            if module == SystemModule.LABORATORY:
                module_actions.extend(LABORATORY_WORKFLOW_ACTIONS)
                module_actions.extend(LABORATORY_RESULTS_ACTIONS)
            if module == SystemModule.BILLING:
                module_actions.extend(BILLING_EXTRA_ACTIONS)
            if module == SystemModule.FINANCE:
                module_actions.extend(FINANCE_EXTRA_ACTIONS)
            if module == SystemModule.REPORTS:
                module_actions.extend(REPORTS_EXTRA_ACTIONS)
            if module == SystemModule.SETTINGS:
                module_actions.extend(SETTINGS_EXTRA_ACTIONS)
            if module == SystemModule.DOCTORS:
                module_actions.extend(DOCTORS_EXTRA_ACTIONS)
            if module == SystemModule.NOTIFICATIONS:
                module_actions.extend(NOTIFICATIONS_EXTRA_ACTIONS)
            for action in module_actions:
                codename = f"{module}.{action}"
                permission, _ = ModulePermission.objects.get_or_create(
                    module=module,
                    action=action,
                    defaults={
                        "codename": codename,
                        "name": f"{module.label} — {action.label}",
                    },
                )
                permissions[codename] = permission

        self.stdout.write(self.style.SUCCESS(f"{len(permissions)} permissões garantidas."))

        for role_value, role_label in UserRole.choices:
            role, _ = Role.objects.get_or_create(
                slug=role_value,
                defaults={
                    "name": role_label,
                    "is_system": True,
                    "description": f"Perfil padrão: {role_label}",
                },
            )
            role.permissions.clear()
            codes = DEFAULT_ROLE_PERMISSIONS.get(role_value, [])
            if codes == "__all__":
                role.permissions.set(permissions.values())
            else:
                role.permissions.set([permissions[c] for c in codes if c in permissions])

        self.stdout.write(self.style.SUCCESS("Perfis padrão configurados."))

        from apps.users.models import UserGroup

        for name, description, role_slug in DEFAULT_GROUPS:
            group, _ = UserGroup.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            role = Role.objects.filter(slug=role_slug).first()
            if role:
                group.permissions.set(role.permissions.all())

        self.stdout.write(self.style.SUCCESS("Grupos padrão configurados."))
