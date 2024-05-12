# Generated by Django 5.0.2 on 2024-05-11 07:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logs", "0009_alter_anomalousevent_fact_datetime"),
    ]

    operations = [
        migrations.AddField(
            model_name="logfile",
            name="one_time_scan",
            field=models.BooleanField(
                default=False, verbose_name="Одноразовое сканирование"
            ),
        ),
    ]