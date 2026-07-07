from django.contrib import admin

from apps.notifications.models import (
    FilaNotificacao,
    HistoricoEmail,
    HistoricoSMS,
    Notificacao,
    PreferenciaNotificacao,
    TemplateEmail,
    TemplateSMS,
)

admin.site.register(Notificacao)
admin.site.register(TemplateEmail)
admin.site.register(TemplateSMS)
admin.site.register(PreferenciaNotificacao)
admin.site.register(HistoricoEmail)
admin.site.register(HistoricoSMS)
admin.site.register(FilaNotificacao)
