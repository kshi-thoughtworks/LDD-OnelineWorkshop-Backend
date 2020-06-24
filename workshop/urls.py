from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls import url

from workshop.services import CardService, ElementService
from . import services

urlpatterns = [
    path('users/register', services.register_user, name='register'),
    path('users/login', services.login_user, name='login'),
    path('users', services.list_users, name='users'),
    path('workbenches', services.workbenches_ops, name='workbenches_ops'),
    path('workbenches/<int:workbench_id>', services.workbenches_ops_by_id, name='workbenches_ops_by_id'),
    path('workbenches/<int:workbench_id>/users', services.users_in_workbench, name='users_in_workbench'),
    path('elements/sticker', ElementService.elements_stickers_ops, name='elements_stickers_ops'),
    path('elements/card', ElementService.elements_cards_ops, name='elements_cards_ops'),
    path('elements/<int:element_id>', ElementService.elements_ops_by_id, name='elements_ops_by_id'),
    path('elements/<int:element_id>/copy', ElementService.copy_element_by_id, name='copy_element_by_id'),
    path('steps/<int:step_id>/elements', ElementService.list_elements_by_step, name='list_elements_by_step'),
    path('cards', CardService.get_cards, name='get_cards'),
    path('cards/tools', CardService.get_tools_cards, name='get_tools_cards'),
    path('cards/types', CardService.get_card_types, name='get_card_types'),
    path('cards/types/<str:card_tpye>', CardService.get_cards_by_type, name='get_cards_by_type'),
    url(r'^.*?$', TemplateView.as_view(template_name='index.html')),
]
