# Generated by Django 4.2.13 on 2024-07-03 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("digitalSociety", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="citizens",
            name="picture",
            field=models.ImageField(
                default="default.png",
                upload_to="profile_pictures/<django.db.models.fields.CharField>",
            ),
        ),
        migrations.AddField(
            model_name="citizens",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
