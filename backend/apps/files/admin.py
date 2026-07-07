"""Admin de ficheiros e documentos."""

from django.contrib import admin

from apps.files.models import StoredFile


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = ("name", "mime_type", "size", "uploaded_by", "created_at")
    list_filter = ("mime_type",)
    search_fields = ("name",)
