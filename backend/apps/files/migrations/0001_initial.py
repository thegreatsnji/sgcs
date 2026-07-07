# Generated manually for Sprint 3.5

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StoredFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Nome")),
                ("file", models.FileField(upload_to="documents/", verbose_name="Ficheiro")),
                ("mime_type", models.CharField(blank=True, max_length=100, verbose_name="Tipo MIME")),
                ("size", models.PositiveIntegerField(default=0, verbose_name="Tamanho (bytes)")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_files",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Carregado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ficheiro",
                "verbose_name_plural": "Ficheiros",
                "ordering": ["-created_at"],
            },
        ),
    ]
