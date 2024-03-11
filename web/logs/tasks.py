from main.celery import app
import time
from celery import shared_task
from logs.models import LogFile, AnomalousLogEvent
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import os
# from django.conf import settings
# from main.settings import CHANNEL_LAYERS

PATTERN = "AUTH ERROR"
# channel_layer = get_channel_layer()
# print(channel_layer.__dict__)

def prepare_lines(lines):
    stripped_lines = map(str.strip, lines)
    non_empty_lines = [line for line in stripped_lines if line]
    return non_empty_lines

@shared_task
def analyze_log_lines(log_file_id, lines: list[str]):
    prepared_lines = prepare_lines(lines)
    # channel_layer = get_channel_layer()
    # logging.info(channel_layer.__dict__)
    # logging.info(prepared_lines)
    for line in prepared_lines:
        if PATTERN in line:
            log_file = LogFile.objects.get(id=log_file_id)
            AnomalousLogEvent.objects.create(text=line, log_file=log_file)
        #     pass
        # message = "ПАЛУНДРА:", datetime.datetime.now().strftime('%H:%M:%S'), line.strip()
        # logging.warning("AAAAA Я ПЕРЕД ОТПРАВКОЙ")
        # async_to_sync(channel_layer.group_send)("logs", message={
        #     "type": "websocket.broadcast",
        #     "message": message
        # })
        # logging.warning("AAAAA Я ПОСЛЕ ОТПРАВКИ")

@shared_task
def read_log_file_task():
    log_files = LogFile.objects.all()
    for log_file in log_files:
        with open("H://Dev//real-time-log-analizer//log_files_test//" + log_file.path, mode="r") as file:
            if not log_file.last_positions:
                file.seek(0, 2)
            else:
                file.seek(log_file.last_positions)
            new_lines = file.readlines()
            new_position = file.tell()
            log_file.last_positions = new_position
            log_file.save()
            analyze_log_lines.delay(log_file.id, new_lines)
