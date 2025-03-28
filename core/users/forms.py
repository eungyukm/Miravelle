from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError


"""회원가입 화면에 나올 List의 Form"""
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
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise ValidationError("비밀번호가 일치하지 않습니다.")

        return cleaned_data


"""로그인 화면에 나올 List의 Form"""
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="ID",  # Username -> ID로 변경
        widget=forms.TextInput(attrs={'autofocus': True})
    )