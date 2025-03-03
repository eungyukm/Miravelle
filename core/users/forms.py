from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="ID",  # Username -> ID로 변경
        widget=forms.TextInput(attrs={'autofocus': True})
    )