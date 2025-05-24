from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Wprowadź poprawny adres e-mail.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class VerificationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['name', 'last_name', 'pesel_num', 'address', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię i nazwisko'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nazwisko'}),
            'pesel_num': forms.TextInput(attrs={'maxlength': 11, 'placeholder': 'PESEL'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
        }

    def clean_pesel_num(self):
        pesel_num = self.cleaned_data.get('pesel_num')
        if Voter.objects.filter(pesel_num=pesel_num).exists():
            raise forms.ValidationError("Ten numer PESEL już istnieje w bazie danych.")
        return pesel_num



class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['address', 'phone_number']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
        }

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