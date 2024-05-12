from django.db import models
from django.utils import timezone
from enum import Enum

class SearchPatternTypeChoices(Enum):
    SIMPLE = "По полному вхождению"
    REGEX = "Регулярное выражение"
    COEFFICIENT = "Словарный коэффициент вхождения"

    @classmethod
    def choices(cls):
        return tuple((role.name, role.value) for role in cls)

class SearchPattern(models.Model):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name="Краткое понятное название или описание"
    )
    pattern = models.CharField(
        verbose_name="Поисковый паттерн", max_length=255
    )
    search_type = models.CharField(
        verbose_name="Тип поиска",
        max_length=255,
        choices=SearchPatternTypeChoices.choices(),
        null=False,
        blank=False
    )

    class Meta:
        verbose_name_plural = "Поисковые паттерны"
        verbose_name = "Поисковый паттерн"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} ({self.get_search_type_display().lower()})"
    

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
        verbose_name="Текст", max_length=255
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

    class Meta:
        verbose_name_plural = "Аномальные события лог-файла"
        verbose_name = "Аномальное событие лог-файла"
        ordering = ("-id",)

    def __str__(self):
        return self.text
