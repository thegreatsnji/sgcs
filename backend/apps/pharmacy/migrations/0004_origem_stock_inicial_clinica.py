from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharmacy", "0003_sprint22_stock_urgencia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movimentostockurgencia",
            name="origem",
            field=models.CharField(
                choices=[
                    ("MANUAL", "Manual"),
                    ("STOCK_INICIAL", "Stock inicial"),
                    ("STOCK_INICIAL_CLINICA", "Stock inicial da clínica"),
                    ("IMPORTACAO", "Importação"),
                ],
                default="MANUAL",
                max_length=32,
                verbose_name="Origem",
            ),
        ),
    ]
