from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls import url

from . import services

urlpatterns = [
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
    path('users', services.list_users, name='users'),
    path('workbenches', services.list_workbenches_by_user, name='list_workbenches_by_user'),
    path('workbenches/<int:workbench_id>/users', services.users_in_workbench, name='users_in_workbench'),
    path('workbench', services.create_workbench, name='workbench'),
    path('workbench/<int:workbench_id>', services.workbench_ops, name='workbench'),
    path('workbench/<int:workbench_id>/users',services.get_workbench_users, name='workbench'),
    url(r'^.*?$', TemplateView.as_view(template_name='index.html')),
]
