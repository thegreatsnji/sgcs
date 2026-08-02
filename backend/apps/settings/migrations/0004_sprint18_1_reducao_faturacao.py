# Sprint 18.1 — configuração de reduções na receção

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic_settings", "0003_sprint16_catalogo"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="permitir_reducao_rececao",
            field=models.BooleanField(default=True, verbose_name="Permitir redução na receção"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="limite_reducao_rececao_percentual",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Deixar vazio até a clínica definir o limite.",
                max_digits=5,
                null=True,
                verbose_name="Limite de redução na receção (%)",
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="exigir_motivo_reducao",
            field=models.BooleanField(default=True, verbose_name="Exigir motivo de redução"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="exigir_autorizacao_acima_limite",
            field=models.BooleanField(
                default=True, verbose_name="Exigir autorização acima do limite"
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="permitir_valor_zero",
            field=models.BooleanField(default=False, verbose_name="Permitir valor cobrado zero"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="exigir_observacao_acima_percentual",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=5,
                null=True,
                verbose_name="Exigir observação acima de (%)",
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="notificar_director_reducao",
            field=models.BooleanField(
                default=False, verbose_name="Notificar direção sobre reduções"
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_reducao_no_recibo",
            field=models.BooleanField(
                default=False,
                verbose_name="Mostrar redução no recibo entregue ao paciente",
            ),
        ),
    ]
