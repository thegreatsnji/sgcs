from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reception", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="receptioncheckin",
            name="age_at_check_in",
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Idade na triagem"),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="blood_pressure",
            field=models.CharField(blank=True, max_length=20, verbose_name="Pressão arterial"),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="symptoms",
            field=models.TextField(blank=True, verbose_name="Sintomas"),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="temperature",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=4,
                null=True,
                verbose_name="Temperatura (°C)",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="triage_color",
            field=models.CharField(
                blank=True,
                choices=[("GREEN", "Verde"), ("YELLOW", "Amarelo"), ("RED", "Vermelho")],
                max_length=10,
                verbose_name="Cor de triagem",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="weight",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=5,
                null=True,
                verbose_name="Peso (kg)",
            ),
        ),
    ]
