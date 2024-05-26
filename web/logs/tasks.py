from celery import shared_task
from logs.models import LogFile, AnomalousEvent
from users.models import User
import os
from django.core.mail import send_mail
import pathlib
import datetime
from main.settings import MTS_SMS_API_URL, MTS_API_KEY, MTS_NUMBER, MTS_CALL_API_URL, MTS_CALL_SERVICE_ID
import requests
from core.utils import notificate_selector
import re
from zoneinfo import ZoneInfo

def prepare_lines(lines: list[str]) -> list[str]:
    """Подготавливает строки к анализу.
    
    Принимает список строк, убирает переносы и пустые строки,
    затем возвращает подготовленный список строк.
    """
    stripped_lines = map(str.strip, lines)
    non_empty_lines = [line for line in stripped_lines if line]
    return non_empty_lines

@shared_task
def analyze_log_lines(log_file_id: int, lines: list[str]) -> None:
    """Анализирует строки на предмет аномальных событий.

    Проходится по каждой строке, определяет,
    является ли строка аномальной, используя паттерны,
    создаёт записи в таблице аномальных событий,
    если строка является аномальной.
    """
    prepared_lines = prepare_lines(lines)
    log_file = LogFile.objects.get(id=log_file_id)
    log_file_type = log_file.type
    search_patterns = log_file_type.search_patterns.all()
    datetime_regex_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    ip_regex_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    for line in prepared_lines:
        print(f'LOG FILE: {log_file} | SCAN LINE: "{line}"')

        datetime_of_line = re.search(datetime_regex_pattern, line)
        if datetime_of_line:
            datetime_end_slice = datetime_of_line.end()
            line = line[datetime_end_slice:]
            datetime_of_line = datetime.datetime.strptime(datetime_of_line.group(0), "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(key='Asia/Yekaterinburg'))
        
        ip_of_line = re.search(ip_regex_pattern, line)
        if ip_of_line:
            ip_of_line = ip_of_line.group(0)
        print(ip_of_line)

        for search_pattern in search_patterns:
            if search_pattern.search_type == "SIMPLE":
                if search_pattern.pattern in line:
                    if search_pattern.counter:
                        anomalous_event, created = AnomalousEvent.objects.get_or_create(
                            text__icontains=ip_of_line, log_file=log_file,
                            count_of_events__gt=0,
                            count_of_events__lt=search_pattern.count_of_events,
                        )

                        if created:
                            anomalous_event.text = line
                            anomalous_event.count_of_events = 1
                            anomalous_event.fact_datetime = datetime_of_line
                        else:
                            # if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime.datetime.now(tz=ZoneInfo(key='Asia/Yekaterinburg')):
                            if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
                                anomalous_event.count_of_events += 1
                            else:
                                anomalous_event.delete()
                                continue


                        if anomalous_event.count_of_events >= search_pattern.count_of_events:
                            anomalous_event.count_of_events = 0
                            notification_types = search_pattern.notification_types.all()
                            notificate_selector(anomalous_event, notification_types)

                        anomalous_event.save()

                    else:
                        anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file, fact_datetime=datetime_of_line, count_of_events=0)
                        notification_types = search_pattern.notification_types.all()
                        notificate_selector(anomalous_event, notification_types)

            elif search_pattern.search_type == "REGEX":
                found = re.search(search_pattern.pattern, line)
                if found:
                    anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file, fact_datetime=datetime_of_line)
                    notification_types = search_pattern.notification_types.all()
                    notificate_selector(anomalous_event, notification_types)
            elif search_pattern.search_type == "COEFFICIENT":
                words = search_pattern.pattern.split()
                coefficient = search_pattern.coefficient
                words_found = 0
                words_count = len(words)
                for word in words:
                    if word in line:
                        words_found += 1
                if (words_found / words_count) >= coefficient:

                    if search_pattern.counter:
                        anomalous_event, created = AnomalousEvent.objects.get_or_create(
                            text__icontains=ip_of_line, log_file=log_file,
                            count_of_events__gt=0,
                            count_of_events__lt=search_pattern.count_of_events,
                        )
                        print(created)
                        print(anomalous_event)

                        if created:
                            anomalous_event.text = line
                            anomalous_event.count_of_events = 1
                            anomalous_event.fact_datetime = datetime_of_line
                        else:
                            # if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime.datetime.now(tz=ZoneInfo(key='Asia/Yekaterinburg')):
                            if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
                                anomalous_event.count_of_events += 1
                                print("+ COUNT")
                            else:
                                print("- DELETE")
                                anomalous_event.delete()
                                continue


                        if anomalous_event.count_of_events >= search_pattern.count_of_events:
                            print('! MATCH')
                            anomalous_event.count_of_events = 0
                            notification_types = search_pattern.notification_types.all()
                            notificate_selector(anomalous_event, notification_types)

                        anomalous_event.save()

                    else:
                        anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file, fact_datetime=datetime_of_line, count_of_events=0)
                        notification_types = search_pattern.notification_types.all()
                        notificate_selector(anomalous_event, notification_types)

                    # anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file, fact_datetime=datetime_of_line)
                    # notification_types = search_pattern.notification_types.all()
                    # notificate_selector(anomalous_event, notification_types)

@shared_task
def read_log_files_task() -> None:
    """Анализирует лог-файлы на предмет новых строк.

    Проходится по каждому лог-файлу в поиске новых строк,
    которые будут переданы в функцию построчного анализа
    с использованием паттернов.
    """
    log_files = LogFile.objects.filter(one_time_scan=False)
    for log_file in log_files:
        with open(os.path.join("/outer", log_file.path[1:]), mode="r") as file:
            if not log_file.last_positions:
                file.seek(0, 2)
            else:
                file.seek(log_file.last_positions)
            new_lines = file.readlines()
            new_position = file.tell()
            log_file.last_positions = new_position
            log_file.save()
            analyze_log_lines.delay(log_file.id, new_lines)

@shared_task
def read_log_file_task(log_file_id: int) -> None:
    """Анализирует конкретный лог-файл на предмет новых строк.

    Проходится по каждому лог-файлу в поиске новых строк,
    которые будут переданы в функцию построчного анализа
    с использованием паттернов.
    """
    log_file = LogFile.objects.get(id=log_file_id)
    with open(os.path.join("/outer", log_file.path[1:]), mode="r") as file:
        # if not log_file.last_positions:
        #     file.seek(0, 2)
        # else:
        #     file.seek(log_file.last_positions)
        lines = file.readlines()
        # new_position = file.tell()
        # log_file.last_positions = new_position
        # log_file.save()
        analyze_log_lines.delay(log_file.id, lines)
