from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reception", "0002_triage_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="receptioncheckin",
            name="height_cm",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Altura (cm)",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="spo2",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="SpO₂ (%)",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="heart_rate",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="FC (b/min)",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="respiratory_rate",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="FR (c/min)",
            ),
        ),
        migrations.AddField(
            model_name="receptioncheckin",
            name="race",
            field=models.CharField(blank=True, max_length=80, verbose_name="Raça"),
        ),
    ]
