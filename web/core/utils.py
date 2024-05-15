from django.core.mail import send_mail
from main.settings import MTS_SMS_API_URL, MTS_API_KEY, MTS_NUMBER, MTS_CALL_API_URL, MTS_CALL_SERVICE_ID
import requests

def email_notificate(anomalous_event, users):
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
    text = f'AN. EV. "{anomalous_event.log_file}": {anomalous_event.text}'
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
            