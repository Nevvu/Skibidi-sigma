from django.core.mail import send_mail
from .models import Notification
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

"""
Generator tokenów do aktywacji konta użytkownika.
Umożliwia tworzenie i weryfikację bezpiecznych tokenów aktywacyjnych przesyłanych w linkach e-mailowych.
"""
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

account_activation_token = AccountActivationTokenGenerator()

"""
Wysyła e-mail z powiadomieniem do wskazanych odbiorców.
Używane do informowania użytkowników o ważnych zdarzeniach, np. rejestracji, aktywacji konta, wynikach wyborów.
"""
def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

"""
Tworzy powiadomienie systemowe dla użytkownika.
Przechowuje tytuł i treść powiadomienia, które mogą być wyświetlane w panelu użytkownika.
"""
def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)
    