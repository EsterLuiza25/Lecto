from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("avatar/", views.avatar, name="avatar"),
    path("avatar/comprar/<int:option_id>/", views.purchase_avatar_option, name="avatar_purchase"),
]
