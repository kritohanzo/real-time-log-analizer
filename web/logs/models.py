from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum

class SearchPatternTypeChoices(Enum):
    SIMPLE = "По полному вхождению"
    REGEX = "Регулярное выражение"
    COEFFICIENT = "Словарный коэффициент вхождения"

    @classmethod
    def choices(cls):
        return tuple((role.name, role.value) for role in cls)


class NotificationType(models.Model):
    description = models.CharField(
        max_length=64, verbose_name="Описание", null=False, blank=False
    )
    method = models.CharField(
        max_length=64, verbose_name="Метод оповещения",
        null=False, blank=False, unique=True
    )

    class Meta:
        verbose_name_plural = "Типы оповещений"
        verbose_name = "Тип оповещения"
        ordering = ("id",)

    def __str__(self):
        return self.description
    

class SearchPattern(models.Model):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name="Краткое понятное название или описание"
    )
    pattern = models.CharField(
        verbose_name="Поисковый паттерн", max_length=4096
    )
    search_type = models.CharField(
        verbose_name="Тип поиска",
        max_length=255,
        choices=SearchPatternTypeChoices.choices(),
        null=False,
        blank=False
    )
    notification_types = models.ManyToManyField(
        NotificationType, through="SearchPatternNotificationType",
        verbose_name="Типы оповещений", related_name="search_patterns",
    )
    counter = models.BooleanField(
        verbose_name="Повторяющееся событие", default=False
    )
    # only for coefficient search type
    coefficient = models.FloatField(
        verbose_name="Словарный коэффициент вхождения",
        null=True,
        default=None,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ]
    )
    # only for count events if counter field is True
    count_of_events = models.IntegerField(
        verbose_name="Количество событий до оповещения",
        null=True, default=0
    )
    period_of_events = models.TimeField(
        verbose_name="Период для подсчёта количества событий до оповещения",
        null=True, default=None
    )

    class Meta:
        verbose_name_plural = "Поисковые паттерны"
        verbose_name = "Поисковый паттерн"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} ({self.get_search_type_display().lower()})"
    

class SearchPatternNotificationType(models.Model):
    search_pattern = models.ForeignKey(
        SearchPattern, on_delete=models.SET_NULL,
        null=True, related_name="search_pattern_notification_types",
        verbose_name="Поисковый паттерн типа оповещения"
    )
    notification_type = models.ForeignKey(
        NotificationType, on_delete=models.SET_NULL,
        null=True, related_name="notification_type_search_patterns",
        verbose_name="Тип оповещения поискового паттерна"
    )

    class Meta:
        verbose_name_plural = "Связи поисковых паттернов и типов оповещений"
        verbose_name = "Связь поискового паттерна и типа оповещения"
        ordering = ("id",)

    def __str__(self):
        return f"Поисковый паттерн '{self.search_pattern}' использует тип оповещения '{self.notification_type}'"


class LogType(models.Model):
    name = models.CharField(
        verbose_name="Краткое понятное название или описание", max_length=255
    )
    search_patterns = models.ManyToManyField(
        SearchPattern,
        through="LogTypeSearchPattern",
        related_name="log_types",
        verbose_name="Подвязанные поисковые паттерны"
    )

    class Meta:
        verbose_name_plural = "Типы протоколов / ПО лог-файла"
        verbose_name = "Тип протокола / ПО лог-файла"
        ordering = ("id",)

    def __str__(self):
        return self.name


class LogTypeSearchPattern(models.Model):
    log_type = models.ForeignKey(
        LogType, on_delete=models.SET_NULL, null=True, related_name="log_type_search_patterns"
    )
    search_pattern = models.ForeignKey(
        SearchPattern, on_delete=models.SET_NULL, null=True, related_name="search_pattern_log_types"
    )

    class Meta:
        verbose_name_plural = "Связи типов протокола / ПО и поисковых паттернов"
        verbose_name = "Связь типа протокола / ПО и поискового паттерна"
        ordering = ("id",)

    def __str__(self):
        return f"Тип протокола / ПО '{self.log_type}' использует поисковый паттерн '{self.search_pattern}'"


class LogFile(models.Model):
    name = models.CharField(verbose_name="Краткое понятное название или описание", max_length=255)
    path = models.CharField(verbose_name="Физический путь до файла", max_length=255)
    type = models.ForeignKey(
        LogType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="log_files",
    )
    one_time_scan = models.BooleanField(
        verbose_name="Одноразовое сканирование",
        default=False
    )
    last_positions = models.IntegerField(
        verbose_name="Последняя позиция при чтении", default=0
    )

    class Meta:
        verbose_name_plural = "Лог-файлы"
        verbose_name = "Лог-файл"
        ordering = ("id",)

    def __str__(self):
        return self.name


class AnomalousEvent(models.Model):
    text = models.CharField(
        verbose_name="Текст", max_length=2048
    )
    fact_datetime = models.DateTimeField(
        verbose_name="Фактическое дата и время", null=True, blank=True
    )
    detected_datetime = models.DateTimeField(
        verbose_name="Дата и время обнаружения", auto_now_add=True
    )
    log_file = models.ForeignKey(
        LogFile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalous_log_events",
    )
    count_of_events = models.IntegerField(
        verbose_name="Количество событий в рамках периода",
        null=True,
        default=None
    )

    class Meta:
        verbose_name_plural = "Аномальные события лог-файла"
        verbose_name = "Аномальное событие лог-файла"
        ordering = ("-id",)

    def __str__(self):
        return self.text
