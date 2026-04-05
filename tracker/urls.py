from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import dashboard, health_check, landing, login_view, signup_view


urlpatterns = [
    path("", landing, name="home"),
    path("healthz/", health_check, name="health_check"),
    path("dashboard/", dashboard, name="dashboard"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
