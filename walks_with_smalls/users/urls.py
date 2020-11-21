from django.contrib.auth import views as auth_views
from django.urls import path, include
from django_registration.backends.one_step.views import RegistrationView

from users.forms import UserRegistrationForm

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("auth/", include("social_django.urls", namespace="social")),
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=UserRegistrationForm),
        name="django_registration_register",
    ),
    path("accounts/", include("django_registration.backends.one_step.urls")),
]
