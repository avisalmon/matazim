# Generated by Django 3.0.8 on 2020-11-11 10:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learn', '0002_registration_last_completion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='hebrew',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL),
        ),
    ]