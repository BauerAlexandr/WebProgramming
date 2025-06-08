from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    date_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)