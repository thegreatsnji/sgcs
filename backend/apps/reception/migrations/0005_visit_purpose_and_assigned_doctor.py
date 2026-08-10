from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("reception", "0004_age_category_at_check_in"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="receptioncheckin",
            name="visit_purpose",
            field=models.CharField(
                blank=True,
                choices=[("CONSULTA", "Consulta"), ("CONTROLE", "Controlo")],
                default="CONSULTA",
                max_length=12,
                verbose_name="Motivo da visita",
            ),
        ),
        migrations.AddField(
            model_name="referral",
            name="assigned_doctor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="referrals_assigned",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Médico atribuído",
            ),
        ),
    ]
