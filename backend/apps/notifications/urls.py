"""URLs do módulo Notificações."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import (
    EmailViewSet,
    NotificacaoViewSet,
    PreferenciaView,
    SMSViewSet,
    TemplateEmailViewSet,
    TemplateSMSViewSet,
)

app_name = "notifications"

router = DefaultRouter()
router.register(r"", NotificacaoViewSet, basename="notification")
router.register(r"email", EmailViewSet, basename="notification-email")
router.register(r"sms", SMSViewSet, basename="notification-sms")
router.register(r"templates/email", TemplateEmailViewSet, basename="template-email")
router.register(r"templates/sms", TemplateSMSViewSet, basename="template-sms")

urlpatterns = [
    path("preferences/", PreferenciaView.as_view(), name="preferences"),
    path("", include(router.urls)),
]
