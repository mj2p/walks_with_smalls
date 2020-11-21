from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
