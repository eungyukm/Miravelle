from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

# 회원 가입 form ()
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=50, label="Name")
    surname = forms.CharField(max_length=50, label="Surname")
    email = forms.EmailField(label="Email")
    message = forms.CharField(widget=forms.Textarea, label="Message", required=False) # 필수 항목 아님

    class Meta:
        model = get_user_model()
        fields = ("username", "surname", "email", "message") + UserCreationForm.Meta.fields