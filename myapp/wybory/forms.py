from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import *
#from captcha.fields import ReCaptchaField
#from captcha.widgets import ReCaptchaV2Checkbox


"""
Formularz rejestracji nowego użytkownika.
Rozszerza domyślny formularz Django o dodatkowe pola lub walidacje, jeśli są wymagane.
"""
class CustomUserCreationForm(UserCreationForm):
   # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ten adres e-mail jest już używany.")
        return email

"""
Formularz służący do przesyłania danych lub dokumentów w celu weryfikacji tożsamości użytkownika.
"""
class VerificationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['name', 'last_name', 'birth_date', 'pesel_num', 'address', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nazwisko'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'pesel_num': forms.TextInput(attrs={'maxlength': 11, 'placeholder': 'PESEL'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
        }
        labels = {
            'name': 'Imię',
            'last_name': 'Nazwisko',
            'birth_date': 'Data urodzenia',
            'pesel_num': 'PESEL',
            'address': 'Adres',
            'phone_number': 'Numer telefonu',
        }

"""
Formularz umożliwiający edycję danych osobowych i kontaktowych użytkownika w profilu wyborcy.
"""
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['address', 'phone_number']  
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
        }
        labels = {
            'address': 'Adres',
            'phone_number': 'Numer telefonu',
        }

"""
Formularz do oddania głosu na wybranego kandydata w określonych wyborach.
Zawiera pole wyboru kandydata i walidację uprawnień.
"""
class CastVoteForm(forms.Form):
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Wybierz kandydata"
    )

    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        super().__init__(*args, **kwargs)
        if election:
            self.fields['candidate'].queryset = Candidate.objects.filter(election=election)

"""
Formularz do oddania głosu na wybraną partię w wyborach parlamentarnych.
Zawiera pole wyboru partii i walidację uprawnień.
"""   
class PartyVoteForm(forms.Form):
    party = forms.ModelChoiceField(
        queryset=Party.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Wybierz partię"
    )

    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        super().__init__(*args, **kwargs)
        if election:
            self.fields['party'].queryset = Party.objects.filter(election=election)





