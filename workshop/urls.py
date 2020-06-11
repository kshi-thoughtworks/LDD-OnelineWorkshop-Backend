from django.urls import path

from . import services

urlpatterns = [
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
    path('users', services.list_users, name='users'),
    path('workbenches', services.list_workbenches_by_user, name='list_workbenches_by_user'),
    path('workbenches/<int:workbench_id>/users', services.list_users_by_workbench, name='list_users_by_workbench'),
    path('workbench', services.create_workbench, name='workbench'),
    path('workbench/<int:workbench_id>', services.get_workbench_by_id, name='workbench'),
    path('user_workbenches', services.add_user_to_workbench, name='list_users_by_workbench'),
]
