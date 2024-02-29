from django.db import models
from django.utils import timezone


class LogFileType(models.Model):
    name = models.CharField(
        verbose_name="Название типа лог-файла", max_length=64
    )

    class Meta:
        verbose_name_plural = "Типы лог-файла"
        verbose_name = "Тип лог-файла"
        ordering = ("name",)

    def __str__(self):
        return self.name


class LogFile(models.Model):
    name = models.CharField(verbose_name="Название лог-файла", max_length=255)
    path = models.CharField(verbose_name="Путь до лог-файла", max_length=255)
    type = models.ForeignKey(
        LogFileType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="log_files",
    )

    class Meta:
        verbose_name_plural = "Лог-файлы"
        verbose_name = "Лог-файл"
        ordering = ("id",)

    def __str__(self):
        return self.name


class AnomalousLogEvent(models.Model):
    text = models.CharField(
        verbose_name="Текст события лог-файла", max_length=255
    )
    datetime = models.DateTimeField(
        verbose_name="Дата и время события лог-файла", default=timezone.now()
    )
    log_file = models.ForeignKey(
        LogFile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalous_log_events",
    )

    class Meta:
        verbose_name_plural = "Аномальные события лог-файла"
        verbose_name = "Аномальное событие лог-файла"
        ordering = ("datetime",)

    def __str__(self):
        return self.text
