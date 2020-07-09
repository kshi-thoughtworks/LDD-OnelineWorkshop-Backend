import logging

from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from marshmallow.exceptions import ValidationError

from workshop.enums import Card_type
from workshop.models import Step, Element, Card
from workshop.schemas import CreateSticker, CreateCard, UpdateElement
from workshop.decorators import my_require_http_methods
from workshop.services.card_service import CardService

UNIQUE_ERROR_PREFIX = "UNIQUE constraint failed"

logger = logging.getLogger(__name__)


class ElementService:

    @staticmethod
    @my_require_http_methods(['POST'])
    def elements_stickers_ops(request):
        return ElementService.elements_ops(request, CreateSticker)

    @staticmethod
    @my_require_http_methods(['POST'])
    def elements_cards_ops(request):
        return ElementService.elements_ops(request, CreateCard)

    @staticmethod
    def elements_ops(request, createElement):
        try:
            createElement = createElement.Schema().loads(request.body)
            element = Element(type=createElement.type,
                              content=createElement.content,
                              title=createElement.title,
                              step=Step.objects.get(pk=createElement.step_id),
                              created_by=request.user,
                              version=0,
                              meta=createElement.meta)
            if createElement.card_id is not None:
                element.card = Card.objects.get(pk=createElement.card_id)
            element.save()
            response = {
                "element_id": element.id,
                "version": element.version
            }
            return JsonResponse(response)
        except ValidationError as e:
            return HttpResponse(e, status=400)
        except Exception as e:
            return HttpResponse(e, status=500)

    @staticmethod
    @my_require_http_methods(['POST'])
    def elements_stickers_ops(request):
        return ElementService.elements_ops(request, CreateSticker)

    @staticmethod
    @my_require_http_methods(['POST'])
    def elements_cards_ops(request):
        return ElementService.elements_ops(request, CreateCard)

    @staticmethod
    @my_require_http_methods(['POST'])
    def copy_element_by_id(request, element_id):
        try:
            oldElement = Element.objects.get(pk=element_id)

            element = Element(type=oldElement.type,
                              title=oldElement.title,
                              content=oldElement.content,
                              step=Step.objects.get(pk=oldElement.step_id),
                              created_by=request.user,
                              version=0
                              )
            if oldElement.card_id is not None:
                element.card = Card.objects.get(pk=oldElement.card_id)
                newMeta = oldElement.meta.to_python(oldElement.meta)
                newMeta["x"] = int(newMeta["x"]) + int(newMeta["width"])
                newMeta["y"] = int(newMeta["y"]) + int(newMeta["height"])
                element.meta = oldElement.meta.get_prep_value(newMeta)
            element.save()
            response = {
                "element_id": element.id,
                'type': element.type,
                'title': element.title,
                'content': element.content,
                'step_id': element.step.id,
                'card': element.card.name if element.card is not None else '',
                'meta': element.meta,
                "version": element.version,
                'created_by': element.created_by.id
            }
            return JsonResponse(response)
        except Exception as e:
            return HttpResponse(e, status=500)

    @staticmethod
    @my_require_http_methods(['GET', 'PUT', 'DELETE'])
    def elements_ops_by_id(request, element_id):
        try:
            element = Element.objects.get(pk=element_id)
            if request.method == 'GET':
                return ElementService.get_element_by_id(element)
            if request.method == 'PUT':
                return ElementService.update_element_by_id(element, request)
            if request.method == 'DELETE':
                return ElementService.delete_element_by_id(element)
        except ValidationError as e:
            return HttpResponse(e, status=400)

    @staticmethod
    def get_element_by_id(element):
        return JsonResponse({
            'type': element.type,
            'title': element.title,
            'content': element.content,
            'step_id': element.step.id,
            'card': element.card.name if element.card is not None else '',
            'meta': element.meta,
            "version": element.version,
            'created_by': element.created_by.id})

    @staticmethod
    def update_element_by_id(element, request):
        update_element = UpdateElement.Schema().loads(request.body)

        if update_element.title.strip(' ') is not None:
            element.title = update_element.title.strip(' ')
        if update_element.content.strip(' ') is not None and update_element.version is not None:
            if update_element.version != element.version:
                return HttpResponse('Incorrect version', status=422)
            element.content = update_element.content.strip(' ')
            element.version = element.version + 1
        if update_element.meta is not None:
            element.meta = update_element.meta
        element.save()
        return HttpResponse()

    @staticmethod
    def delete_element_by_id(element):
        if element is not None:
            element.delete()
        return HttpResponse()

    @staticmethod
    def get_element_data(element: Element):
        data = {
            'id': element.id,
            'type': element.type,
            'title': element.title,
            'content': element.content,
            'step_id': element.step.id,
            'meta': element.meta,
            "version": element.version,
            'created_by': element.created_by.id
        }
        if element.card is not None:
            data['card'] = CardService.get_card(element.card)
        return data

    @staticmethod
    @my_require_http_methods(['GET'])
    def list_elements_by_step(request, step_id):
        elements = Element.objects.filter(step_id=step_id)
        elements_data = list(map(ElementService.get_element_data, elements))
        return JsonResponse(elements_data, safe=False)

    @staticmethod
    @my_require_http_methods(['GET'])
    def list_cards_by_step_and_type(request, step_id, card_tpye):
        elements = Element.objects.filter(Q(step_id=step_id) & Q(card__type__exact=card_tpye))
        elements_data = list(map(ElementService.get_element_data, elements))
        return JsonResponse(elements_data, safe=False)
