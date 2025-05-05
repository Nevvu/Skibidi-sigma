from django.contrib import admin
from django.shortcuts import render, redirect
from django.db.models import Count  
import datetime  
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from .utils import send_notification_email
from .forms import CustomUserCreationForm
from .utils import create_notification
from .utils import create_notification

def election_results(request):
    completed_elections = Election.objects.filter(end_time__lte=datetime.datetime.now())

    results = []
    for election in completed_elections:
        votes = Vote.objects.filter(election=election).values('candidate__name').annotate(vote_count=Count('id')).order_by('-vote_count')
        winner = votes.first() if votes else None
        results.append({
            'election': election,
            'winner': winner['candidate__name'] if winner else "Brak głosów",
            'votes': votes,
        })

        title = f"Wyniki wyborów: {election.title}"
        message = f"Wybory \"{election.title}\" zostały zakończone. Zwycięzca: {winner['candidate__name'] if winner else 'Brak głosów'}."
        for voter in Voter.objects.all():
            create_notification(voter.user, title, message)

    return render(request, 'wybory/public/results.html', {'results': results})

def approve_verification(self, request, queryset):
    for voter in queryset:
        voter.verification_status = 'approved'
        voter.eligible = True
        voter.save()

        title = "Twoja weryfikacja została zatwierdzona"
        message = "Twoja weryfikacja została pomyślnie zatwierdzona. Możesz teraz brać udział w głosowaniach."
        create_notification(voter.user, title, message)

class ElectionAdmin(admin.ModelAdmin):

    list_display = ('title', 'date', 'end_time', 'generate_pdf')

    def generate_pdf(self, obj):
        url = reverse('election_summary_pdf', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Generuj PDF</a>', url)
    generate_pdf.short_description = 'Podsumowanie PDF'


class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'pesel_num', 'eligible', 'verification_status')
    list_filter = ('eligible', 'verification_status')  
    search_fields = ('name', 'email', 'pesel_num')  
    readonly_fields = ('email',)  
    actions = ['approve_verification', 'reject_verification'] 

    def approve_verification(self, request, queryset):
        for voter in queryset:
            voter.verification_status = 'approved'
            voter.eligible = True
            voter.save()
    approve_verification.short_description = 'Zatwierdź wybranych użytkowników'

    def reject_verification(self, request, queryset):
        for voter in queryset:
            voter.verification_status = 'rejected'
            voter.eligible = False
            voter.save()
    reject_verification.short_description = 'Odrzuć wybranych użytkowników'

class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'candidate', 'timestamp')  
    readonly_fields = ('election', 'candidate', 'timestamp')  
    exclude = ('voter',)  



def approve_verification(self, request, queryset):
    for voter in queryset:
        voter.verification_status = 'approved'
        voter.eligible = True
        voter.save()

        subject = "Twoja weryfikacja została zatwierdzona"
        message = f"Witaj {voter.name},\n\nTwoja weryfikacja została pomyślnie zatwierdzona. Możesz teraz brać udział w głosowaniach.\n\nPozdrawiamy,\nZespół Wybory"
        send_notification_email(subject, message, [voter.email])

approve_verification.short_description = 'Zatwierdź wybranych użytkowników'


def election_results(request):
    completed_elections = Election.objects.filter(end_time__lte=datetime.datetime.now())

    results = []
    for election in completed_elections:
        votes = Vote.objects.filter(election=election).values('candidate__name').annotate(vote_count=Count('id')).order_by('-vote_count')
        winner = votes.first() if votes else None
        results.append({
            'election': election,
            'winner': winner['candidate__name'] if winner else "Brak głosów",
            'votes': votes,
        })

        subject = f"Wyniki wyborów: {election.title}"
        message = f"Wybory \"{election.title}\" zostały zakończone.\n\nZwycięzca: {winner['candidate__name'] if winner else 'Brak głosów'}\n\nDziękujemy za udział!"
        recipient_list = [voter.email for voter in Voter.objects.all()]
        send_notification_email(subject, message, recipient_list)

    return render(request, 'wybory/public/results.html', {'results': results})


def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()

        subject = "Witamy w systemie wyborczym"
        message = f"Cześć {user.username},\n\nDziękujemy za rejestrację w naszym systemie wyborczym. Możesz teraz zweryfikować swoje konto, aby brać udział w głosowaniach.\n\nPozdrawiamy,\nZespół Wybory"
        send_notification_email(subject, message, [user.email])

        return redirect('login')
    return render(request, 'wybory/public/signup.html', {'form': form})

admin.site.register(Election, ElectionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Candidate)
admin.site.register(VotingCriteria)
admin.site.register(ElectionType)
admin.site.register(Party)


