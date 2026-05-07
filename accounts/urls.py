from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("cadastro/", views.signup, name="signup"),
    path("entrar/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.profile, name="profile"),
]
