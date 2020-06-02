from django.urls import path

from . import services

urlpatterns = [
    path('users', services.list_users, name='users'),
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
    path('workshops', services.get_workshop_by_user, name='workshops'),
]
