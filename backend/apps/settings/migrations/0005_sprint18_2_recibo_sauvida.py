# Sprint 18.2 — configuração do recibo SauVida

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic_settings", "0004_sprint18_1_reducao_faturacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="formato_recibo",
            field=models.CharField(
                choices=[("A4", "A4"), ("A5", "A5"), ("TERMICO_80", "Térmico 80 mm")],
                default="A4",
                max_length=20,
                verbose_name="Formato do recibo",
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_ministerio_saude_recibo",
            field=models.BooleanField(
                default=False,
                verbose_name="Mostrar referência ao Ministério da Saúde Pública",
            ),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_preco_oficial_recibo",
            field=models.BooleanField(default=False, verbose_name="Mostrar preço oficial no recibo"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_reducao_recibo",
            field=models.BooleanField(default=False, verbose_name="Mostrar linha de redução no recibo"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_saldo_recibo",
            field=models.BooleanField(default=True, verbose_name="Mostrar saldo pendente no recibo"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="mostrar_valor_por_extenso",
            field=models.BooleanField(default=False, verbose_name="Mostrar valor por extenso no recibo"),
        ),
        migrations.AddField(
            model_name="configuracaofaturacao",
            name="texto_rodape_recibo",
            field=models.TextField(blank=True, verbose_name="Texto do rodapé do recibo"),
        ),
    ]
