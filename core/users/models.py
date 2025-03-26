from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True) # ID
    surname = models.CharField(max_length=50) # Name
    email = models.EmailField(unique=True) # 중복 불가
    message = models.TextField(null=True)