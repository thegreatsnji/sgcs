from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pharmacy", "0001_initial"),
        ("patients", "0001_initial"),
        ("appointments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicamentourgencia",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("MEDICAMENTO", "Medicamento"),
                    ("MATERIAL_CLINICO", "Material clínico"),
                    ("TESTE_RAPIDO", "Teste rápido"),
                    ("OUTRO", "Outro"),
                ],
                default="MEDICAMENTO",
                max_length=30,
                verbose_name="Categoria",
            ),
        ),
        migrations.AddField(
            model_name="medicamentourgencia",
            name="validade",
            field=models.DateField(blank=True, null=True, verbose_name="Validade"),
        ),
        migrations.AddField(
            model_name="medicamentourgencia",
            name="preco_referencia_fcfa",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                verbose_name="Preço de referência (FCFA)",
            ),
        ),
        migrations.AddField(
            model_name="medicamentourgencia",
            name="quantidade_texto_original",
            field=models.CharField(
                blank=True,
                help_text="Texto das fotografias (ex.: CX/50). Não é saldo físico.",
                max_length=40,
                verbose_name="Quantidade (texto original)",
            ),
        ),
        migrations.AlterField(
            model_name="movimentostockurgencia",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("ENTRADA", "Entrada"),
                    ("SAIDA", "Saída"),
                    ("AJUSTE", "Ajuste de inventário"),
                    ("PERDA_EXPIRACAO", "Perda / expiração"),
                ],
                max_length=20,
                verbose_name="Tipo",
            ),
        ),
        migrations.AddField(
            model_name="movimentostockurgencia",
            name="origem",
            field=models.CharField(
                choices=[
                    ("MANUAL", "Manual"),
                    ("STOCK_INICIAL", "Stock inicial"),
                    ("IMPORTACAO", "Importação"),
                ],
                default="MANUAL",
                max_length=20,
                verbose_name="Origem",
            ),
        ),
        migrations.AddField(
            model_name="movimentostockurgencia",
            name="paciente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="movimentos_stock_urgencia",
                to="patients.patient",
                verbose_name="Utente",
            ),
        ),
        migrations.AddField(
            model_name="movimentostockurgencia",
            name="consulta",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="movimentos_stock_urgencia",
                to="appointments.appointment",
                verbose_name="Consulta",
            ),
        ),
    ]
