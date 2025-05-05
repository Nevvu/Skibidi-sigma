from django.core.mail import send_mail
from .models import Notification


def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'twoj_email@gmail.com',  # Nadawca (EMAIL_HOST_USER z settings.py)
        recipient_list,
        fail_silently=False,
    )



def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)