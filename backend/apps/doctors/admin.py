"""Administração Django — módulo médico."""

from django.contrib import admin

from apps.doctors.models import (
    AltaMedica,
    EvolucaoClinica,
    MedicamentoPrescrito,
    PlanoTerapeutico,
    Prescricao,
    SeguimentoClinico,
    Tratamento,
)

admin.site.register(Prescricao)
admin.site.register(MedicamentoPrescrito)
admin.site.register(PlanoTerapeutico)
admin.site.register(Tratamento)
admin.site.register(EvolucaoClinica)
admin.site.register(AltaMedica)
admin.site.register(SeguimentoClinico)
