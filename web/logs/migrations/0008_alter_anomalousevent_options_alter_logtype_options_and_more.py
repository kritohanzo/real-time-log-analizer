# Generated by Django 5.0.2 on 2024-05-09 06:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logs", "0007_searchpattern_name_alter_anomalousevent_datetime_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="anomalousevent",
            options={
                "ordering": ("-id",),
                "verbose_name": "Аномальное событие лог-файла",
                "verbose_name_plural": "Аномальные события лог-файла",
            },
        ),
        migrations.AlterModelOptions(
            name="logtype",
            options={
                "ordering": ("id",),
                "verbose_name": "Тип протокола / ПО лог-файла",
                "verbose_name_plural": "Типы протоколов / ПО лог-файла",
            },
        ),
        migrations.RemoveField(
            model_name="anomalousevent",
            name="datetime",
        ),
        migrations.AddField(
            model_name="anomalousevent",
            name="detected_datetime",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата и время обнаружения",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="anomalousevent",
            name="fact_datetime",
            field=models.DateTimeField(
                null=True, verbose_name="Фактическое дата и время"
            ),
        ),
    ]