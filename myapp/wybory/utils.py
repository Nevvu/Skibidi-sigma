from django.core.mail import send_mail
from .models import Notification
from django.conf import settings

def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

# def send_notification_email(subject, message, recipient_list):
#     print(f"Sending email to {recipient_list}")
#     try:
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             recipient_list,
#             fail_silently=False,
#         )
#     except Exception as e:
#         print(f"Email send failed: {e}")


def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)
    