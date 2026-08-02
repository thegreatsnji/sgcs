# Sprint 18.2 — versão de catálogo e recibo

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0005_sprint18_1_meta"),
    ]

    operations = [
        migrations.AddField(
            model_name="servico",
            name="arquivado",
            field=models.BooleanField(db_index=True, default=False, verbose_name="Arquivado (fora da receção)"),
        ),
        migrations.AddField(
            model_name="servico",
            name="versao_catalogo",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Ex.: SAUVIDA_V1 — vazio para legado",
                max_length=40,
                verbose_name="Versão do catálogo",
            ),
        ),
        migrations.AddField(
            model_name="recibo",
            name="segunda_via",
            field=models.BooleanField(default=False, verbose_name="Segunda via"),
        ),
    ]
