# Generated by Django 3.0.8 on 2020-08-28 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0013_auto_20200828_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='last_completion',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='learn.Completion'),
        ),
    ]
