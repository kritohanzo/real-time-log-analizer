# Generated by Django 5.0.2 on 2024-02-29 17:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anomalouslogevent",
            name="datetime",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 2, 29, 17, 13, 20, 660780, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Дата и время события лог-файла",
            ),
        ),
    ]