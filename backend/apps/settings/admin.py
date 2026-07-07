"""Administração Django — configurações."""

from django.contrib import admin

from apps.settings.models import (
    BackupRegisto,
    ClinicSetting,
    ConfiguracaoEmail,
    ConfiguracaoFaturacao,
    ConfiguracaoFicheiros,
    ConfiguracaoSeguranca,
    ConfiguracaoSms,
    Consultorio,
    Departamento,
    EspecialidadeMedica,
    FeatureFlag,
    Feriado,
    HorarioFuncionamento,
    PerfilClinica,
    TipoConsulta,
    TipoExameLaboratorio,
)

admin.site.register(ClinicSetting)
admin.site.register(PerfilClinica)
admin.site.register(EspecialidadeMedica)
admin.site.register(Departamento)
admin.site.register(Consultorio)
admin.site.register(HorarioFuncionamento)
admin.site.register(Feriado)
admin.site.register(TipoConsulta)
admin.site.register(TipoExameLaboratorio)
admin.site.register(ConfiguracaoFaturacao)
admin.site.register(ConfiguracaoEmail)
admin.site.register(ConfiguracaoSms)
admin.site.register(ConfiguracaoSeguranca)
admin.site.register(ConfiguracaoFicheiros)
admin.site.register(FeatureFlag)
admin.site.register(BackupRegisto)
