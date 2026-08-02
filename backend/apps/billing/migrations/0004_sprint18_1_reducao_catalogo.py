# Sprint 18.1 — redução de valores na fatura e autorizações

import django.db.models.deletion
from decimal import Decimal

from django.conf import settings
from django.db import migrations, models


def backfill_item_preco_oficial(apps, schema_editor):
    ItemFatura = apps.get_model("billing", "ItemFatura")
    for item in ItemFatura.objects.iterator():
        item.preco_oficial = item.preco
        item.subtotal_oficial = item.subtotal
        item.save(update_fields=["preco_oficial", "subtotal_oficial"])


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0003_sprint17_preco_confirmado"),
        ("patients", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="itemfatura",
            name="preco_oficial",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Preço oficial (un.)",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="subtotal_oficial",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Subtotal oficial",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="valor_reducao",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Valor da redução (total linha)",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="percentual_reducao",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=7,
                verbose_name="Percentual de redução",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="motivo_reducao",
            field=models.CharField(
                blank=True,
                choices=[
                    ("DIFICULDADE_FINANCEIRA", "Dificuldade financeira do paciente"),
                    ("APOIO_SOCIAL", "Apoio social"),
                    ("PACIENTE_CARENCIADO", "Paciente carenciado"),
                    ("DESCONTO_DIRECAO", "Desconto autorizado pela Direção"),
                    ("CAMPANHA_CLINICA", "Campanha da clínica"),
                    ("FUNCIONARIO_FAMILIAR", "Funcionário ou familiar"),
                    ("PAGAMENTO_PARCIAL", "Pagamento parcial negociado"),
                    ("CORTESIA", "Cortesia"),
                    ("OUTRO", "Outro"),
                ],
                max_length=40,
                verbose_name="Motivo da redução",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="observacao_reducao",
            field=models.TextField(blank=True, verbose_name="Observação da redução"),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="origem_preco",
            field=models.CharField(
                choices=[
                    ("CATALOGO", "Catálogo"),
                    ("REDUCAO_RECECAO", "Redução na receção"),
                    ("REDUCAO_AUTORIZADA", "Redução autorizada"),
                    ("CAMPANHA", "Campanha"),
                    ("GRATUITO_AUTORIZADO", "Gratuito autorizado"),
                    ("OUTRO", "Outro"),
                ],
                default="CATALOGO",
                max_length=30,
                verbose_name="Origem do preço cobrado",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="estado_autorizacao_reducao",
            field=models.CharField(
                choices=[
                    ("NAO_APLICAVEL", "Não aplicável"),
                    ("APROVADA_AUTOMATICAMENTE", "Aprovada automaticamente"),
                    ("PENDENTE", "Pendente"),
                    ("APROVADA", "Aprovada"),
                    ("REJEITADA", "Rejeitada"),
                    ("CANCELADA", "Cancelada"),
                ],
                default="NAO_APLICAVEL",
                max_length=30,
                verbose_name="Estado da autorização",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="data_reducao",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Data da redução"),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="autorizado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="itens_fatura_reducao_autorizados",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Autorizado por",
            ),
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="reduzido_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="itens_fatura_reduzidos",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Redução aplicada por",
            ),
        ),
        migrations.AlterField(
            model_name="itemfatura",
            name="preco",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Snapshot do valor efectivamente cobrado por unidade.",
                max_digits=12,
                verbose_name="Preço cobrado (un.)",
            ),
        ),
        migrations.AlterField(
            model_name="itemfatura",
            name="subtotal",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                verbose_name="Subtotal cobrado",
            ),
        ),
        migrations.CreateModel(
            name="ReducaoValorAutorizacao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("solicitado_em", models.DateTimeField(auto_now_add=True, verbose_name="Solicitado em")),
                (
                    "motivo_reducao",
                    models.CharField(
                        choices=[
                            ("DIFICULDADE_FINANCEIRA", "Dificuldade financeira do paciente"),
                            ("APOIO_SOCIAL", "Apoio social"),
                            ("PACIENTE_CARENCIADO", "Paciente carenciado"),
                            ("DESCONTO_DIRECAO", "Desconto autorizado pela Direção"),
                            ("CAMPANHA_CLINICA", "Campanha da clínica"),
                            ("FUNCIONARIO_FAMILIAR", "Funcionário ou familiar"),
                            ("PAGAMENTO_PARCIAL", "Pagamento parcial negociado"),
                            ("CORTESIA", "Cortesia"),
                            ("OUTRO", "Outro"),
                        ],
                        max_length=40,
                        verbose_name="Motivo",
                    ),
                ),
                (
                    "observacao_solicitacao",
                    models.TextField(blank=True, verbose_name="Observação"),
                ),
                (
                    "preco_oficial",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Preço oficial"
                    ),
                ),
                (
                    "preco_proposto",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Preço proposto"
                    ),
                ),
                ("quantidade", models.PositiveIntegerField(default=1, verbose_name="Quantidade")),
                (
                    "diferenca_unitaria",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Diferença (un.)"
                    ),
                ),
                (
                    "percentual_reducao",
                    models.DecimalField(decimal_places=2, max_digits=7, verbose_name="Percentual"),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("NAO_APLICAVEL", "Não aplicável"),
                            ("APROVADA_AUTOMATICAMENTE", "Aprovada automaticamente"),
                            ("PENDENTE", "Pendente"),
                            ("APROVADA", "Aprovada"),
                            ("REJEITADA", "Rejeitada"),
                            ("CANCELADA", "Cancelada"),
                        ],
                        default="PENDENTE",
                        max_length=30,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "decidido_em",
                    models.DateTimeField(blank=True, null=True, verbose_name="Decidido em"),
                ),
                (
                    "observacao_decisao",
                    models.TextField(blank=True, verbose_name="Observação da decisão"),
                ),
                (
                    "decidido_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reducoes_decididas",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Decidido por",
                    ),
                ),
                (
                    "fatura",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="autorizacoes_reducao",
                        to="billing.fatura",
                        verbose_name="Fatura",
                    ),
                ),
                (
                    "paciente",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="autorizacoes_reducao",
                        to="patients.patient",
                        verbose_name="Paciente",
                    ),
                ),
                (
                    "servico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="autorizacoes_reducao",
                        to="billing.servico",
                        verbose_name="Serviço",
                    ),
                ),
                (
                    "solicitado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reducoes_solicitadas",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Solicitado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "Autorização de redução de valor",
                "verbose_name_plural": "Autorizações de redução de valor",
                "ordering": ["-solicitado_em"],
            },
        ),
        migrations.AddField(
            model_name="itemfatura",
            name="autorizacao_reducao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="itens_fatura",
                to="billing.reducaovalorautorizacao",
                verbose_name="Autorização de redução",
            ),
        ),
        migrations.AddIndex(
            model_name="reducaovalorautorizacao",
            index=models.Index(fields=["estado", "solicitado_em"], name="idx_bill_red_estado"),
        ),
        migrations.RunPython(backfill_item_preco_oficial, migrations.RunPython.noop),
    ]
