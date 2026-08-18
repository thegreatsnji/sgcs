from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="metadata",
            field=models.JSONField(blank=True, default=dict, verbose_name="Metadados"),
        ),
        migrations.AlterField(
            model_name="patient",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="Data de nascimento"),
        ),
        migrations.AlterField(
            model_name="patient",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("M", "Masculino"), ("F", "Feminino"), ("O", "Outro")],
                max_length=1,
                verbose_name="Sexo",
            ),
        ),
        migrations.AlterField(
            model_name="patient",
            name="phone",
            field=models.CharField(blank=True, max_length=20, verbose_name="Telefone"),
        ),
    ]
