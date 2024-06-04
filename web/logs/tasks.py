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
    date_regex_pattern_1 = r"\d{2,4}-\d{2,4}-\d{2,4}"
    date_regex_pattern_2 = r"\d{2,4}.\d{2,4}.\d{2,4}"
    date_regex_pattern_3 = r"\d{2,4}/\d{2,4}/\d{2,4}"
    time_regex_pattern_1 = r"\d{2}:\d{2}:\d{2}"
    time_regex_pattern_2 = r"\d{2}-\d{2}-\d{2}"
    ip_regex_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    for line in prepared_lines:
        print(f'LOG FILE: {log_file} | SCAN LINE: "{line}"')

        date_of_line = re.search(date_regex_pattern_1, line)
        if not date_of_line:
            date_of_line = re.search(date_regex_pattern_2, line)
        if not date_of_line:
            date_of_line = re.search(date_regex_pattern_3, line)

        time_of_line = re.search(time_regex_pattern_1, line)
        if not time_of_line:
            time_of_line = re.search(time_regex_pattern_2, line)

        if date_of_line and time_of_line:
            datetime_of_line = date_of_line.group(0) + " " + time_of_line.group(0)

            if "-" in date_of_line.group(0):
                splitter = "-"
            elif "/" in date_of_line.group(0):
                splitter = "/"
            else:
                splitter = "."

            if len(date_of_line.group(0).split(splitter)[0]) == 4:
                date_format = splitter.join(["%Y", "%m", "%d"])
            else:
                date_format = splitter.join(["%d", "%m", "%Y"])

            time_format = "%H:%M:%S" if ":" in time_of_line.group(0) else "%H-%M-%S"
            datetime_format = date_format + " " + time_format
            try:
                datetime_of_line = datetime.datetime.strptime(datetime_of_line, datetime_format).replace(tzinfo=ZoneInfo(key='Asia/Yekaterinburg'))
            except:
                print("CAN NOT PARSE FACT DATETIME")
                datetime_of_line = None
        else:
            print("CAN NOT PARSE FACT DATETIME")
            datetime_of_line = None
        
        ip_of_line = re.search(ip_regex_pattern, line)
        if ip_of_line:
            ip_of_line = f" {ip_of_line.group(0)} "
        print(ip_of_line)

        for search_pattern in search_patterns:
            if search_pattern.search_type == "SIMPLE":
                if search_pattern.pattern in line:
                    if search_pattern.counter:
                        anomalous_event, created = AnomalousEvent.objects.get_or_create(
                            text__icontains=ip_of_line, log_file=log_file,
                            count_of_events__isnull=False,
                            count_of_events__lt=search_pattern.count_of_events,
                            detected_search_pattern=search_pattern
                        )

                        if created:
                            anomalous_event.text = line
                            anomalous_event.count_of_events += 1
                            anomalous_event.fact_datetime = datetime_of_line
                        else:
                            if not anomalous_event.fact_datetime and anomalous_event.log_file.one_time_scan:
                                print("CAN NOT GET FACT DATETIME, SKIP LINE")
                                continue

                            if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
                                anomalous_event.count_of_events += 1
                            else:
                                anomalous_event.delete()
                                continue


                        if anomalous_event.count_of_events >= search_pattern.count_of_events:
                            anomalous_event.count_of_events = None
                            notification_types = search_pattern.notification_types.all()
                            notificate_selector(anomalous_event, notification_types)

                        anomalous_event.save()

                    else:
                        anomalous_event = AnomalousEvent.objects.create(
                            text=line, log_file=log_file, fact_datetime=datetime_of_line,
                            count_of_events=None, detected_search_pattern=search_pattern
                        )
                        notification_types = search_pattern.notification_types.all()
                        notificate_selector(anomalous_event, notification_types)

            elif search_pattern.search_type == "REGEX":
                found = re.search(search_pattern.pattern, line)
                if found:
                    if search_pattern.counter:
                        anomalous_event, created = AnomalousEvent.objects.get_or_create(
                            text__icontains=ip_of_line, log_file=log_file,
                            count_of_events__isnull=False,
                            count_of_events__lt=search_pattern.count_of_events,
                            detected_search_pattern=search_pattern
                        )

                        if created:
                            anomalous_event.text = line
                            anomalous_event.count_of_events += 1
                            anomalous_event.fact_datetime = datetime_of_line
                        else:
                            if not anomalous_event.fact_datetime and anomalous_event.log_file.one_time_scan:
                                print("CAN NOT GET FACT DATETIME, SKIP LINE")
                                continue

                            if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
                                anomalous_event.count_of_events += 1
                            else:
                                anomalous_event.delete()
                                continue


                        if anomalous_event.count_of_events >= search_pattern.count_of_events:
                            anomalous_event.count_of_events = None
                            notification_types = search_pattern.notification_types.all()
                            notificate_selector(anomalous_event, notification_types)

                        anomalous_event.save()

                    else:
                        anomalous_event = AnomalousEvent.objects.create(
                            text=line, log_file=log_file, fact_datetime=datetime_of_line,
                            count_of_events=None, detected_search_pattern=search_pattern
                        )
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
                            count_of_events__isnull=False,
                            count_of_events__lt=search_pattern.count_of_events,
                            detected_search_pattern=search_pattern
                        )

                        if created:
                            anomalous_event.text = line
                            anomalous_event.count_of_events += 1
                            anomalous_event.fact_datetime = datetime_of_line
                        else:
                            if not anomalous_event.fact_datetime and anomalous_event.log_file.one_time_scan:
                                print("CAN NOT GET FACT DATETIME, SKIP LINE")
                                continue

                            if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
                                anomalous_event.count_of_events += 1
                            else:
                                anomalous_event.delete()
                                continue


                        if anomalous_event.count_of_events >= search_pattern.count_of_events:
                            anomalous_event.count_of_events = None
                            notification_types = search_pattern.notification_types.all()
                            notificate_selector(anomalous_event, notification_types)

                        anomalous_event.save()

                    else:
                        anomalous_event = AnomalousEvent.objects.create(
                            text=line, log_file=log_file, fact_datetime=datetime_of_line,
                            count_of_events=None, detected_search_pattern=search_pattern
                        )
                        notification_types = search_pattern.notification_types.all()
                        notificate_selector(anomalous_event, notification_types)

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
