# Generated manually — Sprint 17 confirmação de preços

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_sprint16_catalogo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="servico",
            name="preco_confirmado",
            field=models.BooleanField(default=False, verbose_name="Preço confirmado pela clínica"),
        ),
        migrations.AddField(
            model_name="servico",
            name="preco_confirmado_em",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Preço confirmado em"),
        ),
        migrations.AddField(
            model_name="servico",
            name="preco_confirmado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="servicos_preco_confirmado",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Preço confirmado por",
            ),
        ),
        migrations.AddField(
            model_name="servico",
            name="permite_faturacao_sem_preco_confirmado",
            field=models.BooleanField(
                default=False,
                verbose_name="Autorização temporária de faturação (admin)",
            ),
        ),
        migrations.AddIndex(
            model_name="servico",
            index=models.Index(fields=["preco_confirmado", "activo"], name="idx_bill_svc_preco_conf"),
        ),
    ]
