from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_func, name="login_page"),
    path("logout/", views.logout_func, name="logout_page"),
    path("signup/", views.signup_func, name="signup_page"),
]