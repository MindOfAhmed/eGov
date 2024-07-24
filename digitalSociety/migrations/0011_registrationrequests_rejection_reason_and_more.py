# Generated by Django 4.2.13 on 2024-07-24 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("digitalSociety", "0010_vehicles"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationrequests",
            name="rejection_reason",
            field=models.TextField(blank=True, default="not rejected", null=True),
        ),
        migrations.AddField(
            model_name="renewalrequests",
            name="rejection_reason",
            field=models.TextField(blank=True, default="not rejected", null=True),
        ),
        migrations.AlterField(
            model_name="drivinglicenses",
            name="nationality",
            field=models.CharField(default="X", max_length=30),
        ),
        migrations.CreateModel(
            name="Notifications",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                (
                    "citizen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="digitalSociety.citizens",
                    ),
                ),
            ],
        ),
    ]
