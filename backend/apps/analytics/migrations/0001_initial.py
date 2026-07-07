# Generated manually for Sprint 3.5

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_name", models.CharField(max_length=100, verbose_name="Evento")),
                ("payload", models.JSONField(blank=True, default=dict, verbose_name="Dados")),
                ("recorded_at", models.DateTimeField(auto_now_add=True, verbose_name="Registado em")),
            ],
            options={
                "verbose_name": "Evento de analytics",
                "verbose_name_plural": "Eventos de analytics",
                "ordering": ["-recorded_at"],
            },
        ),
    ]
