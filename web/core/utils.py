from django.core.mail import send_mail
from main.settings import MTS_SMS_API_URL, MTS_API_KEY, MTS_NUMBER, MTS_CALL_API_URL, MTS_CALL_SERVICE_ID
import requests
import re
import datetime
from logs.models import AnomalousEvent
from zoneinfo import ZoneInfo


def email_notificate(anomalous_event, users):
    """Посылает письмо на почту пользователям.
    
    Пробегает по каждому пользователю и рассылает письмо всем,
    у кого указана почта в списке пользователей.
    """
    recipient_list = [user.email for user in users]
    subject = f'Аномальное событие в лог-файле'
    message = f'В лог-файле "{anomalous_event.log_file}" произошло аномальное событие: "{anomalous_event.text}"'
    print(f'START EMAIL NOTIFICATION TO RECIPIENTS {", ".join(recipient_list)}:', end=" ")
    try:
        send_mail(subject, message, from_email=None, recipient_list=recipient_list)
        print("SENT")
    except:
        print("ERROR")

def sms_notificate(anomalous_event, users):
    """Посылает SMS пользователям.
    
    Пробегает по каждому пользователю и рассылает SMS всем,
    у кого указан номер телефона в списке пользователей.
    """
    text = f'Аномальное событие в лог-файле "{anomalous_event.log_file}": {anomalous_event.text}'
    for user in users:
        destination = user.phone_number.replace("+", "")
        print(f"START SMS NOTIFICATION TO {destination}:", end=" ")
        try:
            response = requests.post(
                MTS_SMS_API_URL,
                headers={
                    "Authorization": f"Bearer {MTS_API_KEY}"
                },
                json={
                    "number": MTS_NUMBER,
                    "destination": destination,  
                    "text": text   
                }
            )
            if response.status_code != 200:
                raise Exception()
            print("SENT")
        except:
            print("ERROR")

def call_notificate(users):
    """Посылает звонок пользователям.
    
    Пробегает по каждому пользователю и рассылает звонки всем,
    у кого указан номер телефона в списке пользователей.
    """
    for user in users:
        destination = user.phone_number.replace("+", "")
        print(f"START CALL NOTIFICATION TO {destination}:", end=" ")
        try:
            response = requests.post(
                MTS_CALL_API_URL,
                headers={
                    "Authorization": f"Bearer {MTS_API_KEY}"
                },
                json={
                    "source": MTS_NUMBER,
                    "destination": destination,  
                    "service_id": MTS_CALL_SERVICE_ID
                }
            )
            if response.status_code != 200:
                raise Exception()
            print("SENT")
        except:
            print("ERROR")

def notificate_selector(anomalous_event, notification_types):
    """Рассылает все возможные виды оповещений.
    
    Пробегает по каждому типу оповещения и,
    опираясь на аномальное событие, рассылает
    все возможные оповещения.
    """
    for notification_type in notification_types:
        if notification_type.method == "email":
            users = notification_type.users.filter(email__isnull=False).exclude(email__exact='')
            email_notificate(anomalous_event, users)
        elif notification_type.method == 'sms':
            users = notification_type.users.filter(phone_number__isnull=False).exclude(phone_number__exact='')
            sms_notificate(anomalous_event, users)
        elif notification_type.method == 'call':
            users = notification_type.users.filter(phone_number__isnull=False).exclude(phone_number__exact='')
            call_notificate(users)
            
def get_ip_from_line(line):
    ip_regex_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"

    ip_of_line = re.search(ip_regex_pattern, line)
    if ip_of_line:
        ip_of_line = f" {ip_of_line.group(0)} "
        return ip_of_line
    return None

def get_datetime_from_line(line):
    date_regex_pattern_1 = r"(?:\d{4}|\d{2})-(?:\d{4}|\d{2})-(?:\d{4}|\d{2})"
    date_regex_pattern_2 = r"(?:\d{4}|\d{2}).(?:\d{4}|\d{2}).(?:\d{4}|\d{2})"
    date_regex_pattern_3 = r"(?:\d{4}|\d{2})/(?:\d{4}|\d{2})/(?:\d{4}|\d{2})"
    time_regex_pattern_1 = r"\d{2}:\d{2}:\d{2}"
    time_regex_pattern_2 = r"\d{2}-\d{2}-\d{2}"

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
            return datetime_of_line
        except:
            print("CAN NOT PARSE FACT DATETIME")
            return None
    else:
        print("CAN NOT PARSE FACT DATETIME")
        return None


def analyze_counter(line, search_pattern, log_file, datetime_of_line, ip_of_line):
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
            return

        if anomalous_event.fact_datetime + datetime.timedelta(hours=search_pattern.period_of_events.hour, minutes=search_pattern.period_of_events.minute, seconds=search_pattern.period_of_events.second) > datetime_of_line:
            anomalous_event.count_of_events += 1
        else:
            anomalous_event.delete()
            return

    if anomalous_event.count_of_events >= search_pattern.count_of_events:
        anomalous_event.count_of_events = None
        notification_types = search_pattern.notification_types.all()
        notificate_selector(anomalous_event, notification_types)

    anomalous_event.save()


def analyze_simple(line, search_pattern, log_file, datetime_of_line, ip_of_line):
    if search_pattern.pattern in line:
        if search_pattern.counter:
            analyze_counter(line, search_pattern, log_file, datetime_of_line, ip_of_line)
        else:
            anomalous_event = AnomalousEvent.objects.create(
                text=line, log_file=log_file, fact_datetime=datetime_of_line,
                count_of_events=None, detected_search_pattern=search_pattern
            )
            notification_types = search_pattern.notification_types.all()
            notificate_selector(anomalous_event, notification_types)


def analyze_regex(line, search_pattern, log_file, datetime_of_line, ip_of_line):
    found = re.search(search_pattern.pattern, line)
    if found:
        if search_pattern.counter:
            analyze_counter(line, search_pattern, log_file, datetime_of_line, ip_of_line)
        else:
            anomalous_event = AnomalousEvent.objects.create(
                text=line, log_file=log_file, fact_datetime=datetime_of_line,
                count_of_events=None, detected_search_pattern=search_pattern
            )
            notification_types = search_pattern.notification_types.all()
            notificate_selector(anomalous_event, notification_types)

def analyze_coefficient(line, search_pattern, log_file, datetime_of_line, ip_of_line):
    words = search_pattern.pattern.split()
    coefficient = search_pattern.coefficient
    words_found = 0
    words_count = len(words)
    for word in words:
        if word in line:
            words_found += 1
    if (words_found / words_count) >= coefficient:
        if search_pattern.counter:
            analyze_counter(line, search_pattern, log_file, datetime_of_line, ip_of_line)
        else:
            anomalous_event = AnomalousEvent.objects.create(
                text=line, log_file=log_file, fact_datetime=datetime_of_line,
                count_of_events=None, detected_search_pattern=search_pattern
            )
            notification_types = search_pattern.notification_types.all()
            notificate_selector(anomalous_event, notification_types)

