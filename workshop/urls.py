from django.urls import path

from . import services

urlpatterns = [
    path('', services.index, name='index'),
    path('users', services.list_users, name='users'),
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
]
