"""Admin de analytics."""

from django.contrib import admin

from apps.analytics.models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "recorded_at")
    list_filter = ("event_name",)
    search_fields = ("event_name",)
