from django.urls import path

from . import services

urlpatterns = [
    path('users', services.list_users, name='users'),
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
    path('workbenches', services.get_workbenches_by_user, name='workshops'),
    path('workbench', services.create_workbench, name='workbench'),
    path('workbench/<int:workbench_id>', services.get_workbench_by_id, name='workbench')
]
