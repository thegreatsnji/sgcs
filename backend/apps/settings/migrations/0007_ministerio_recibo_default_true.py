# Cabeçalho do recibo alinhado ao livro oficial SauVida

from django.db import migrations, models


def activar_ministerio_recibo(apps, schema_editor):
    Config = apps.get_model("clinic_settings", "ConfiguracaoFaturacao")
    Config.objects.all().update(mostrar_ministerio_saude_recibo=True)


class Migration(migrations.Migration):

    dependencies = [
        ("clinic_settings", "0006_catalogo_v1_codigo_length"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuracaofaturacao",
            name="mostrar_ministerio_saude_recibo",
            field=models.BooleanField(
                default=True,
                verbose_name="Mostrar referência ao Ministério da Saúde Pública",
            ),
        ),
        migrations.RunPython(activar_ministerio_recibo, migrations.RunPython.noop),
    ]
