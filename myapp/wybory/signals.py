from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from .utils import create_notification, send_notification_email
from .models import Election, Voter


@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    title = "Logowanie do systemu"
    message = "Zalogowałeś się do systemu. "
    create_notification(user, title, message)


@receiver(pre_save, sender=Voter)
def cache_previous_status(sender, instance, **kwargs):
    if instance.pk:  # Jeśli obiekt już istnieje
        instance._previous_status = instance.__class__.objects.get(pk=instance.pk).verification_status
    else:
        instance._previous_status = None

@receiver(post_save, sender=Voter)
def handle_verification_status_change(sender, instance, created, **kwargs):
    print(f"Sygnał post_save wywołany dla {instance.name} (created={created})")
    if not created and hasattr(instance, '_previous_status'):
        previous_status = instance._previous_status
        print(f"Poprzedni status: {previous_status}, Nowy status: {instance.verification_status}")
        if previous_status != instance.verification_status:
            if instance.verification_status == 'approved':
                print("Wysyłanie powiadomienia o zatwierdzeniu...")
                title = "Twoja weryfikacja została zatwierdzona"
                message = "Twoja weryfikacja została pomyślnie zatwierdzona. Możesz teraz brać udział w głosowaniach."
                create_notification(instance.user, title, message)
                send_notification_email(
                    "Potwierdzenie weryfikacji",
                    f"Witaj {instance.name},\n\n{message}",
                    [instance.email]
                )
            elif instance.verification_status == 'rejected':
                print("Wysyłanie powiadomienia o odrzuceniu...")
                title = "Twoja weryfikacja została odrzucona"
                message = "Twoja weryfikacja została odrzucona. Skontaktuj się z administratorem, aby uzyskać więcej informacji."
                create_notification(instance.user, title, message)
                send_notification_email(
                    "Odrzucenie weryfikacji",
                    f"Witaj {instance.name},\n\n{message}",
                    [instance.email]
                )



@receiver(post_save, sender=Election)
def handle_election_status_change(sender, instance, created, **kwargs):
    if created:
        title = f"Rozpoczęły się wybory: {instance.title}"
        message = f"Rozpoczęły się wybory \"{instance.title}\". Możesz teraz oddać swój głos."
        for voter in Voter.objects.filter(eligible=True):
            create_notification(voter.user, title, message)
            send_notification_email(
                f"Rozpoczęcie wyborów: {instance.title}",
                f"Witaj {voter.name},\n\n{message}",
                [voter.email]
            )
    elif instance.end_time:
        title = f"Zakończyły się wybory: {instance.title}"
        message = f"Wybory \"{instance.title}\" zostały zakończone. Dziękujemy za udział!"
        for voter in Voter.objects.all():
            create_notification(voter.user, title, message)
            send_notification_email(
                f"Zakończenie wyborów: {instance.title}",
                f"Witaj {voter.name},\n\n{message}",
                [voter.email]
            )