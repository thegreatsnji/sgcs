from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reception", "0003_ficha_triage_vitals"),
    ]

    operations = [
        migrations.AddField(
            model_name="receptioncheckin",
            name="age_category_at_check_in",
            field=models.CharField(
                blank=True,
                choices=[("ADULT", "Adulto"), ("MINOR", "Menor de idade")],
                max_length=10,
                verbose_name="Categoria etária na triagem",
            ),
        ),
    ]
