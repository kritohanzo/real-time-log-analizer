from celery import shared_task
from logs.models import LogFile, AnomalousEvent
from users.models import User
import os
from django.core.mail import send_mail
import pathlib
from main.settings import MTS_SMS_API_URL, MTS_API_KEY, MTS_NUMBER, MTS_CALL_API_URL, MTS_CALL_SERVICE_ID
import requests
from core.utils import notificate_selector
import re

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
    for line in prepared_lines:
        print(f'LOG FILE: {log_file} | SCAN LINE: "{line}"')
        for search_pattern in search_patterns:
            if search_pattern.search_type == "SIMPLE":
                if search_pattern.pattern in line:
                    anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file)
                    notification_types = search_pattern.notification_types.all()
                    notificate_selector(anomalous_event, notification_types)
            elif search_pattern.search_type == "REGEX":
                found = re.search(search_pattern.pattern, line)
                if found:
                    anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file)
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
                    anomalous_event = AnomalousEvent.objects.create(text=line, log_file=log_file)
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
