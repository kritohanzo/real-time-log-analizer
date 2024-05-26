from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django import views
import datetime
from logs.forms import LogFileForm, LogTypeForm, SearchPatternForm, AnomalousEventSearchForm, OneTimeScanAnomalousEventSearchForm, LogFileSearchForm, LogTypeSearchForm, SearchPatternSearchForm
from logs.models import LogFile, LogType, SearchPattern, AnomalousEvent, NotificationType
from logs.tasks import read_log_file_task
from qsstats import QuerySetStats
from django.core.paginator import Paginator
from random import randint
from django.utils.timezone import get_current_timezone
from core.utils import notificate_selector
import json
from zoneinfo import ZoneInfo
from django.db.models import Count, F, QuerySet
from django.db.models.functions import Lower
import pytz
from django.core.mail import send_mail
from users.models import User
from main.settings import MTS_API_KEY, MTS_SMS_API_URL, MTS_NUMBER, MTS_CALL_API_URL, MTS_CALL_SERVICE_ID
import requests


class GenerateTestAnomalousEventView(views.View):
    def get(self, request, *args, **kwargs):
        log_files = LogFile.objects.filter(one_time_scan=False)
        if log_files:
            log_file = log_files[randint(0, len(log_files)-1)]
            texts = ["Тестовая строка 1", "Тестовая строка 2", "Тестовая строка 3", "Тестовая строка 4"]
            text = texts[randint(0, len(texts)-1)]
            anomalous_event = AnomalousEvent.objects.create(text=text, log_file=log_file)
            search_patterns = anomalous_event.log_file.type.search_patterns.all()
            for search_pattern in search_patterns:
                notification_types = search_pattern.notification_types.all()
                notificate_selector(anomalous_event, notification_types)
        return render(request, template_name="success.html", context={"message": "Вы успешно сгенерировали аномальное событие"})



class MainPageView(views.View):
    def get(self, request, *args, **kwargs):
        form = AnomalousEventSearchForm()
        start_datetime = datetime.datetime.now(tz=ZoneInfo(key='Asia/Yekaterinburg')).replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime = start_datetime + datetime.timedelta(days=1)
        anomalous_events = AnomalousEvent.objects.filter(detected_datetime__gt=start_datetime, detected_datetime__lt=end_datetime, log_file__one_time_scan=False, count_of_events=0)
        qsstats = QuerySetStats(anomalous_events, date_field='detected_datetime')
        logs_metrics = qsstats.time_series(start_datetime, end_datetime, interval='minutes')
        logs_metrics = list(filter(lambda x: x[1] > 0 or x[0].minute % 30 == 0, logs_metrics))
        logs_metrics = [[str(i[0]), i[1]] for i in logs_metrics]
        return render(request, template_name="logs/index.html", context={"form": form, "logs_metrics": json.dumps(logs_metrics), "start_datetime": start_datetime, "end_datetime": end_datetime, "anomalous_events": anomalous_events[:6]})
    
    def post(self, request, *args, **kwargs):
        form = AnomalousEventSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        text, start_datetime, end_datetime, log_file, log_type, search_pattern = form.cleaned_data.values()
        anomalous_events = AnomalousEvent.objects.filter(detected_datetime__gt=start_datetime, detected_datetime__lt=end_datetime, log_file__one_time_scan=False, count_of_events=0)
        if text:
            anomalous_events = anomalous_events.filter(text__icontains=text)
        if log_file:
            anomalous_events = anomalous_events.filter(log_file=log_file)
        if log_type:
            anomalous_events = anomalous_events.filter(log_file__type=log_type)
        if search_pattern:
            log_types = search_pattern.log_types.all() 
            if log_types:
                anomalous_events = anomalous_events.filter(log_file__type__in=log_types)
        qsstats = QuerySetStats(anomalous_events, date_field='detected_datetime')
        logs_metrics = qsstats.time_series(start_datetime, end_datetime, interval='minutes')
        logs_metrics = list(filter(lambda x: x[1] > 0 or x[0].minute % 30 == 0, logs_metrics))
        logs_metrics = [[str(i[0]), i[1]] for i in logs_metrics]
        return render(request, template_name="logs/index.html", context={"form": form, "logs_metrics": json.dumps(logs_metrics), "start_datetime": start_datetime, "end_datetime": end_datetime, "anomalous_events": anomalous_events[:6]})


# Anomalous Event Views


class AnomalousEventListView(views.View):
    def get(self, request, *args, **kwargs):
        anomalous_events = AnomalousEvent.objects.filter(log_file__one_time_scan=False, count_of_events=0)
        paginator = Paginator(anomalous_events, 50)
        page = paginator.get_page(self.request.GET.get('page'))
        form = AnomalousEventSearchForm()
        return render(request, template_name="logs/anomalous-events/anomalous-events-list.html", context={"form": form, "page": page})

    def post(self, request, *args, **kwargs):
        form = AnomalousEventSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        text, start_datetime, end_datetime, log_file, log_type, search_pattern = form.cleaned_data.values()
        anomalous_events = AnomalousEvent.objects.filter(detected_datetime__gt=start_datetime, detected_datetime__lt=end_datetime, log_file__one_time_scan=False, count_of_events=0)
        if text:
            anomalous_events = anomalous_events.filter(text__icontains=text)
        if log_file:
            anomalous_events = anomalous_events.filter(log_file=log_file)
        if log_type:
            anomalous_events = anomalous_events.filter(log_file__type=log_type)
        if search_pattern:
            anomalous_events = anomalous_events.filter(log_file__type__search_patterns=search_pattern)
        paginator = Paginator(anomalous_events, 50)
        page = paginator.get_page(self.request.GET.get('page'))
        return render(request, template_name="logs/anomalous-events/anomalous-events-list.html", context={"form": form, "page": page})


class AnomalousEventDeleteView(views.View):
    def get(self, request, anomalous_event_id, *args, **kwargs):
        anomalous_event = get_object_or_404(AnomalousEvent, id=anomalous_event_id)
        anomalous_event.delete()
        return render(request, template_name="success.html", context={"message": "Вы успеншо удалили аномальное событие"})


# Log File Views


class LogFileListView(views.View):
    def get(self, request, *args, **kwargs):
        log_files = LogFile.objects.filter(one_time_scan=False)
        form = LogFileSearchForm()
        return render(request, template_name="logs/log-files/log-files-list.html", context={"log_files": log_files, "form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogFileSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        log_files = LogFile.objects.filter(one_time_scan=False)
        name, path, log_type, search_pattern = form.cleaned_data.values()
        print(form.cleaned_data)
        if name:
            log_files = log_files.filter(name__icontains=name)
        if path:
            log_files = log_files.filter(path__icontains=path)
        if log_type:
            log_files = log_files.filter(type=log_type)
        if search_pattern:
            log_files = log_files.filter(type__search_patterns=search_pattern)
        return render(request, template_name="logs/log-files/log-files-list.html", context={"log_files": log_files, "form": form})


class LogFileAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = LogFileForm()
        return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogFileForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form})
        LogFile.objects.create(**form.cleaned_data, one_time_scan=False)
        return render(request, template_name="success.html", context={"message": "Вы успеншо добавили лог-файл"})


class LogFileEditView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        form = LogFileForm(instance=log_file)
        return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form, "log_file_id": log_file_id, "is_edit": True})
    
    def post(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        form = LogFileForm(request.POST, instance=log_file)
        if not form.is_valid():
            return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form, "is_edit": True})
        form.save()
        return render(request, template_name="success.html", context={"message": "Вы успешно изменили лог-файл"})


class LogFileDeleteView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        log_file.delete()
        return render(request, template_name="success.html", context={"message": "Вы успешно удалили лог-файл"})


# Log Type Views


class LogTypeListView(views.View):
    def get(self, request, *args, **kwargs):
        log_types = LogType.objects.all()
        form = LogTypeSearchForm()
        return render(request, template_name="logs/log-types/log-types-list.html", context={"log_types": log_types, "form": form})
    def post(self, request, *args, **kwargs):
        form = LogTypeSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        name, search_pattern = form.cleaned_data.values()
        log_types = LogType.objects.all()
        if name:
            log_types = log_types.filter(name__icontains=name)
        if search_pattern:
            log_types = log_types.filter(search_patterns=search_pattern)
        return render(request, template_name="logs/log-types/log-types-list.html", context={"log_types": log_types, "form": form})
    

class LogTypeAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = LogTypeForm()
        return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogTypeForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form})
        search_patterns = form.cleaned_data.pop("search_patterns")
        log_type = LogType.objects.create(**form.cleaned_data)
        log_type.search_patterns.set(search_patterns)
        return render(request, template_name="success.html", context={"message": "Вы успешно добавили протокол / ПО"})


class LogTypeEditView(views.View):
    def get(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        form = LogTypeForm(instance=log_type)
        return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form, "log_type_id": log_type_id, "is_edit": True})
    
    def post(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        form = LogTypeForm(request.POST, instance=log_type)
        if not form.is_valid():
            return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form, "log_type_id": log_type_id, "is_edit": True})
        form.save()
        search_patterns = form.cleaned_data.pop("search_patterns")
        log_type.search_patterns.set(search_patterns)
        return render(request, template_name="success.html", context={"message": "Вы успешно изменили протокол / ПО"})


class LogTypeDeleteView(views.View):
    def get(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        log_type.delete()
        return render(request, template_name="success.html", context={"message": "Вы успешно удалили протокол / ПО"})
    

# Search Patterns Views


class SearchPatternListView(views.View):
    def get(self, request, *args, **kwargs):
        search_patterns = SearchPattern.objects.all()
        form = SearchPatternSearchForm()
        return render(request, template_name="logs/search-patterns/search-patterns-list.html", context={"search_patterns": search_patterns, "form": form})
    
    def post(self, request, *args, **kwargs):
        form = SearchPatternSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        search_patterns = SearchPattern.objects.all()
        name, pattern, search_type, notification_type = form.cleaned_data.values()
        if name:
            search_patterns = search_patterns.filter(name__icontains=name)
        if pattern:
            search_patterns = search_patterns.filter(pattern__icontains=pattern)
        if search_type:
            search_patterns = search_patterns.filter(search_type=search_type)
        if notification_type:
            search_patterns = search_patterns.filter(notification_types=notification_type)
        return render(request, template_name="logs/search-patterns/search-patterns-list.html", context={"search_patterns": search_patterns, "form": form}) 
    

class SearchPatternAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = SearchPatternForm()
        return render(request, template_name="logs/search-patterns/search-pattern-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = SearchPatternForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/search-patterns/search-pattern-form.html", context={"form": form})
        notification_types = NotificationType.objects.filter(method="websocket") | form.cleaned_data.pop("notification_types")
        search_pattern = SearchPattern.objects.create(**form.cleaned_data)
        search_pattern.notification_types.set(notification_types)
        return render(request, template_name="success.html", context={"message": "Вы успешно добавили поисковый паттерн"})


class SearchPatternEditView(views.View):
    def get(self, request, search_pattern_id, *args, **kwargs):
        search_pattern = get_object_or_404(SearchPattern, id=search_pattern_id)
        form = SearchPatternForm(instance=search_pattern)
        return render(request, template_name="logs/search-patterns/search-pattern-form.html", context={"form": form, "search_pattern_id": search_pattern_id, "is_edit": True})
    
    def post(self, request, search_pattern_id, *args, **kwargs):
        search_pattern = get_object_or_404(SearchPattern, id=search_pattern_id)
        form = SearchPatternForm(request.POST, instance=search_pattern)
        if not form.is_valid():
            return render(request, template_name="logs/search-patterns/search-pattern-form.html", context={"form": form, "search_pattern_id": search_pattern_id, "is_edit": True})
        form.save()
        notification_types = NotificationType.objects.filter(method="websocket") | form.cleaned_data.pop("notification_types")
        search_pattern.notification_types.set(notification_types)
        return render(request, template_name="success.html", context={"message": "Вы успешно изменили поисковый паттерн"})


class SearchPatternDeleteView(views.View):
    def get(self, request, search_pattern_id, *args, **kwargs):
        search_pattern = get_object_or_404(SearchPattern, id=search_pattern_id)
        search_pattern.delete()
        return render(request, template_name="success.html", context={"message": "Вы успеншо удалили поисковый паттерн"})
    

# One Time Scan Views


class OneTimeScanListView(views.View):
    def get(self, request, *args, **kwargs):
        log_files = LogFile.objects.filter(one_time_scan=True)
        return render(request, template_name="logs/one-time-scans/one-time-scans-list.html", context={"log_files": log_files})


class OneTimeScanAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = LogFileForm()
        return render(request, template_name="logs/one-time-scans/one-time-scan-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogFileForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/one-time-scans/one-time-scan-form.html", context={"form": form})
        log_file = LogFile.objects.create(**form.cleaned_data, one_time_scan=True)
        read_log_file_task.delay(log_file.id)
        return render(request, template_name="success.html", context={"message": "Вы успешно добавили лог-файл"})


class OneTimeScanDeleteView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        log_file.delete()
        return render(request, template_name="success.html", context={"message": "Вы успешно удалили лог-файл"})
    

class OneTimeScanAnomalousEventListView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        form = OneTimeScanAnomalousEventSearchForm()
        anomalous_events = AnomalousEvent.objects.filter(log_file__id=log_file_id, count_of_events=0)
        paginator = Paginator(anomalous_events, 50)
        page = paginator.get_page(self.request.GET.get('page'))
        return render(request, template_name="logs/one-time-scans/one-time-scan-anomalous-events-list.html", context={"page": page, "form": form, "log_file_id": log_file_id})
    
    def post(self, request, log_file_id, *args, **kwargs):
        form = OneTimeScanAnomalousEventSearchForm(request.POST)
        if not form.is_valid():
            return self.get(self, request, *args, **kwargs)
        anomalous_events = AnomalousEvent.objects.filter(log_file__id=log_file_id, count_of_events=0)
        text = form.cleaned_data.get('text')
        if text:
            anomalous_events = anomalous_events.filter(text__icontains=text)
        paginator = Paginator(anomalous_events, 50)
        page = paginator.get_page(self.request.GET.get('page'))
        return render(request, template_name="logs/one-time-scans/one-time-scan-anomalous-events-list.html", context={"page": page, "form": form, "log_file_id": log_file_id})