from django import forms
from .models import Voter

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



class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['name', 'last_name', 'address', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nazwisko'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adres'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Numer telefonu'}),
        }