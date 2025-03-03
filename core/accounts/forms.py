from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=50, label="ID")
    surname = forms.CharField(max_length=50, label="Name")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Password Confirmation")
    email = forms.EmailField(label="Email")
    message = forms.CharField(widget=forms.Textarea, label="Message", required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "surname", "password1", "password2", "email", "message")