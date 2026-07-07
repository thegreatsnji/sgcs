# Generated manually for Sprint 3.5

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ClinicSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=100, unique=True, verbose_name="Chave")),
                ("value", models.JSONField(default=dict, verbose_name="Valor")),
                ("description", models.TextField(blank=True, verbose_name="Descrição")),
                ("is_active", models.BooleanField(default=True, verbose_name="Ativo")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
            ],
            options={
                "verbose_name": "Configuração",
                "verbose_name_plural": "Configurações",
                "ordering": ["key"],
            },
        ),
    ]
