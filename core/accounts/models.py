from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    surname = models.CharField(max_length=50) # 성씨
    email = models.EmailField(unique=True) # 중복 불가
    message = models.TextField()
