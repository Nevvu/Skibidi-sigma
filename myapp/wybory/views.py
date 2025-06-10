from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from .models import *
from .forms import *
import datetime
from .forms import CustomUserCreationForm, CastVoteForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count
from weasyprint import HTML
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Notification
from wybory.utils import send_notification_email
from wybory.utils import create_notification
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives
from .forms import CustomUserCreationForm as SignUpForm
from .utils import account_activation_token
from django.shortcuts import render
from django.utils.timezone import now, localtime
from django.contrib.auth import login
import requests
from django.conf import settings
import matplotlib.pyplot as plt
import io
import base64
from .models import Voter, VotersLog
from .forms import PartyVoteForm
import logging
import oracledb
logger = logging.getLogger('myapp')
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser


# --- Serializery ---
class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ['id', 'user', 'name', 'email', 'verification_status']

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'title', 'date', 'end_time', 'election_type']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'party', 'election']

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name']

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'candidate', 'election']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active']

# --- ViewSety ---
class VoterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer
    permission_classes = [IsAdminUser]

class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

class CandidateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class PartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

class VoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAdminUser]

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


def my_view(request):
    logger.info("To jest log informacyjny")
    logger.error("Coś poszło nie tak!")


def index(request):
    # logger.info("Strona główna została odwiedzona")
    return render(request, 'signup.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        # Sprawdzenie reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LdREUkrAAAAAGxiNBHatbkyMG8vOY_KpwoP6_Tq',  # NIE PUBLICZNY
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if form.is_valid() and result.get('success'):
            form.save()
            return redirect('login')  # lub inna strona po rejestracji
        else:
            messages.error(request, 'Błąd rejestracji lub nieprawidłowa CAPTCHA.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Aktywuj swoje konto'
            message = render_to_string('wybory/emails/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            send_notification_email(subject, message, [user.email])
            messages.success(request, 'Rejestracja zakończona! Sprawdź e-mail, aby aktywować konto.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'wybory/public/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Dodajemy Voter tylko jeśli nie istnieje
        if not hasattr(user, 'voter'):
            Voter.objects.create(user=user, name=user.username, email=user.email)

        login(request, user)
        messages.success(request, 'Konto zostało aktywowane!')
        return redirect('home')
    else:
        return HttpResponse('Link aktywacyjny jest nieprawidłowy lub wygasł.')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Konto nieaktywne. Sprawdź e-mail.')
        else:
            messages.error(request, 'Nieprawidłowy login lub hasło.')
    return render(request, 'wybory/public/login.html')



def faq(request): return render(request, 'wybory/public/faq.html')
def contact(request): return render(request, 'wybory/public/contact.html')


def election_list(request):
    elections = Election.objects.all()
    return render(request, 'wybory/public/election_list.html', {'elections': elections})

def election_calendar(request):
    elections = Election.objects.filter(date__gte=datetime.date.today()).order_by('date')
    return render(request, 'wybory/public/election_calendar.html', {'elections': elections})

def parties(request):
    parties = Party.objects.all()
    return render(request, 'wybory/public/parties.html', {'parties': parties})

def candidate_list(request, election_id):
    elections = Election.objects.all()
    selected_election_id = str(election_id)
    candidates = Candidate.objects.filter(election_id=election_id)
    parties = Party.objects.filter(election_id=election_id)
    return render(request, 'wybory/public/candidate-list.html', {
        'elections': elections,
        'selected_election_id': selected_election_id,
        'candidates': candidates,
        'parties': parties,
    })

def candidate_search(request):
    elections = Election.objects.all()
    selected_election_id = request.GET.get('election_id')
    candidates = Candidate.objects.none()
    parties = Party.objects.none()
    if selected_election_id:
        candidates = Candidate.objects.filter(election_id=selected_election_id)
        parties = Party.objects.filter(election_id=selected_election_id)
    return render(request, 'wybory/public/candidate-list.html', {
        'elections': elections,
        'selected_election_id': selected_election_id,
        'candidates': candidates,
        'parties': parties,
    })


from django.utils.timezone import localtime, now

def election_results(request):
    try:
        # Połączenie z bazą Oracle (uzupełnij danymi do logowania!)
        conn = oracledb.connect(
            user='app_identity',
            password='App#123',
            dsn='localhost:1521/XEPDB1'
        )
        cur = conn.cursor()
        cur.execute('SELECT ELECTION_ID, TITLE, CANDIDATE_ID, CANDIDATE_NAME, VOTES FROM ELECTION_RESULTS')
        results = [
            {
                'election_id': row[0],
                'title': row[1],
                'candidate_id': row[2],
                'candidate_name': row[3],
                'votes': row[4]
            }
            for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
    except Exception as e:
        return HttpResponse(f"Błąd połączenia z Oracle: {e}")

    return render(request, 'wybory/public/results.html', {'results': results})

# --- Voting process ---


def election_detail(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = election.candidates.all()
    return render(request, 'wybory/voter/election_detail.html', {'election': election, 'candidates': candidates})


from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import redirect, render

from django.utils.timezone import now, localtime

@login_required
def cast_vote(request, election_id):
    voter = Voter.objects.filter(user=request.user).first()
    if not voter or voter.verification_status not in ['eligible', 'approved']:
        messages.error(request, "Nie masz uprawnień do głosowania. Zweryfikuj swoje dane.")
        return redirect('voter_panel')

    election = Election.objects.filter(id=election_id).first()
    if not election:
        messages.error(request, "Nie znaleziono wyborów.")
        return redirect('voter_panel')

    current_time = localtime(now())  
    is_voting_available = election.date <= current_time <= election.end_time


    if not is_voting_available:
        start_time = localtime(election.date).strftime("%d-%m-%Y %H:%M")
        end_time = localtime(election.end_time).strftime("%d-%m-%Y %H:%M")
        messages.error(request, f"Głosowanie jest niedostępne. Możesz głosować tylko między {start_time} a {end_time}.")
        return redirect('voter_panel')
    

    if VotersLog.objects.filter(voter_id=voter.id, election_id=election.id).exists():
        messages.error(request, "Już oddałeś głos w tych wyborach.")
        return redirect('voter_panel')
    
    

    if request.method == 'POST':
        form = CastVoteForm(request.POST, election=election)
        if form.is_valid():
            candidate = form.cleaned_data['candidate']
            try:
                conn = oracledb.connect(
                     user='app_identity',
                    password='App#123',
                    dsn='localhost:1521/XEPDB1'
                )
                cur = conn.cursor()
                cur.callproc('voting_pkg.cast_vote', [voter.id, candidate.id, election.id])
                cur.close()
                conn.close()
                messages.success(request, "Twój głos został oddany!")
                return redirect('ballot')
            except oracledb.DatabaseError as e:
                messages.error(request, f"Błąd bazy Oracle: {e}")
                return redirect('voter_panel')
    else:
        form = CastVoteForm(election=election)

    return render(request, 'wybory/voter/cast_vote.html', {
        'election': election,
        'form': form,
        'is_voting_available': is_voting_available,
    })


# --- Voter-only views ---
@login_required
def voter_panel(request): return render(request, 'wybory/voter/panel.html')



from django.utils.timezone import localtime, now

def ballot(request):
    current_time = localtime(now())
    presidential_elections = Election.objects.filter(
        election_type__name='Prezydenckie',
        end_time__gt=current_time
    )
    parliamentary_elections = Election.objects.filter(
        election_type__name='Parlamentarne',
        end_time__gt=current_time
    )
    # voted_elections i party_voted_elections jak dotychczas
    return render(request, 'wybory/voter/ballot.html', {
        'presidential_elections': presidential_elections,
        'parliamentary_elections': parliamentary_elections,
        # ...pozostałe zmienne...
    })

@login_required
def activity_history(request):
    voted_elections_ids = [
        int(key.split('_')[1]) for key in request.session.keys() if key.startswith('voted_') and request.session[key]
    ]
    voted_elections = Election.objects.filter(id__in=voted_elections_ids)

    return render(request, 'wybory/voter/activity_history.html', {'voted_elections': voted_elections})


@login_required
def profile(request):
    voter = Voter.objects.filter(user=request.user).first()  
    if not voter:
        return redirect('verify_identity')  

    form = EditProfileForm(request.POST or None, instance=voter)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('profile')  

    return render(request, 'wybory/voter/profile.html', {'user': request.user, 'voter': voter, 'form': form})

@login_required
def verify_identity(request):
    voter = Voter.objects.filter(user=request.user).first()
    if not voter:
        voter = Voter.objects.create(user=request.user, name=request.user.username, email=request.user.email)

    form = VerificationForm(request.POST or None, instance=voter)
    if request.method == 'POST' and form.is_valid():
        form.save()
        voter.verification_status = 'pending'  
        voter.save()
        messages.success(request, "Twoje dane zostały przesłane do weryfikacji.")
        send_notification_email("Weryfikacja wyborcy", f"Witaj {voter.name},\n\nTwoje dane zostały przesłane do weryfikacji.", [voter.email])
        title = "Weryfikacja wyborcy"
        message = "Twoje dane zostały przesłane do weryfikacji. Oczekuj na dalsze instrukcje."
        create_notification(request.user, title, message)
        return redirect('voter_panel')  

    return render(request, 'wybory/voter/verify_identity.html', {'form': form})


def generate_election_summary_pdf(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = Candidate.objects.filter(election=election)
    votes = Vote.objects.filter(election=election)

    candidate_support = []
    total_votes = votes.count()
    candidate_names = []
    candidate_votes_list = []

    for candidate in candidates:
        candidate_votes = votes.filter(candidate=candidate).count()
        support_percentage = (candidate_votes / total_votes * 100) if total_votes > 0 else 0
        candidate_support.append({
            'name': candidate.name,
            'party': candidate.party.name if candidate.party else "Bezpartyjny",
            'votes': candidate_votes,
            'support_percentage': round(support_percentage, 2),
        })
        candidate_names.append(candidate.name)
        candidate_votes_list.append(candidate_votes)

    # Generowanie wykresu
    plt.figure(figsize=(6, 6))
    plt.pie(candidate_votes_list, labels=candidate_names, autopct='%1.1f%%', startangle=140)
    plt.title(f"Wyniki wyborów: {election.title}")

    # Zapisanie wykresu do pamięci jako obraz
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Kontekst dla szablonu
    context = {
        'election': election,
        'candidates': candidate_support,
        'start_time': election.date,
        'end_time': election.end_time,
        'total_candidates': candidates.count(),
        'total_votes': total_votes,
        'chart': image_base64,  # Wykres w formacie base64
    }

    # Renderowanie szablonu HTML
    html_string = render_to_string('wybory/pdf/election_summary.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    # Generowanie pliku PDF
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="podsumowanie_wyborow_{election_id}.pdf"'
    return response




@login_required
def notifications(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        print(f"Received notification_id: {notification_id}")  
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        print(f"Notification found: {notification}")  
        if not notification.is_read:
            notification.is_read = True
            notification.save()
            print(f"Notification {notification_id} marked as read")  
        return JsonResponse({'status': 'success', 'message': 'Powiadomienie oznaczone jako przeczytane'})

    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wybory/voter/notifications.html', {'notifications': user_notifications})

from django.contrib.auth.decorators import user_passes_test


def home(request):
    presidential_elections = Election.objects.filter(election_type__name="Prezydenckie")
    parliamentary_elections = Election.objects.filter(election_type__name="Parlamentarne")

    return render(request, 'wybory/public/home.html', {
        'presidential_elections': presidential_elections,
        'parliamentary_elections': parliamentary_elections,
    })


@login_required
def cast_party_vote(request, election_id):
    voter = Voter.objects.filter(user=request.user).first()
    if not voter or voter.verification_status not in ['eligible', 'approved']:
        messages.error(request, "Nie masz uprawnień do głosowania na partię. Zweryfikuj swoje dane.")
        return redirect('voter_panel')

    election = Election.objects.filter(id=election_id).first()
    if not election:
        messages.error(request, "Nie znaleziono wyborów.")
        return redirect('voter_panel')

    current_time = localtime(now()) 
    is_voting_available = election.date <= current_time <= election.end_time

    if not is_voting_available:
        start_time = localtime(election.date).strftime("%d-%m-%Y %H:%M")
        end_time = localtime(election.end_time).strftime("%d-%m-%Y %H:%M")
        messages.error(request, f"Głosowanie na partie jest niedostępne. Możesz głosować tylko między {start_time} a {end_time}.")
        return redirect('voter_panel')

    if request.method == 'POST':
        form = PartyVoteForm(request.POST, election=election)
        if form.is_valid():
            party = form.cleaned_data['party']
            try:
                conn = oracledb.connect(
                    user='app_identity',
                    password='App#123',
                    dsn='localhost:1521/XEPDB1'
                )
                cur = conn.cursor()
                # Wywołanie funkcji SQL obsługującej głosowanie na partię
                result = cur.callfunc('cast_party_vote', int, [voter.id, party.id, election.id])
                cur.close()
                conn.close()
                if result == 1:
                    request.session[f'party_voted_{election_id}'] = True
                    messages.success(request, "Twój głos na partię został oddany pomyślnie.")
                    return redirect('ballot')
                else:
                    messages.error(request, "Nie udało się oddać głosu na partię.")
                    return redirect('voter_panel')
            except oracledb.DatabaseError as e:
                error, = e.args
                # Obsługa wyjątku z RAISE_APPLICATION_ERROR w SQL
                if hasattr(error, 'code') and error.code == 20001:
                    messages.error(request, "Już oddałeś głos w tych wyborach.")
                else:
                    messages.error(request, f"Błąd bazy Oracle: {e}")
                return redirect('voter_panel')
    else:
        form = PartyVoteForm(election=election)

    return render(request, 'wybory/voter/cast_party_vote.html', {
        'election': election,
        'form': form,
        'is_voting_available': is_voting_available,
    })