import logging

from django.http import JsonResponse
from functools import reduce
from django.db.models import Q

from workshop.enums import Card_type, ToolCardTypes
from workshop.models import Card
from workshop.decorators import my_require_http_methods

UNIQUE_ERROR_PREFIX = "UNIQUE constraint failed"

logger = logging.getLogger(__name__)


class CardService:
    @staticmethod
    def get_card(card: Card):
        if card is None:
            return None

        return {
            "id": card.id,
            "name": card.name,
            "type": card.type,
            "sup_type": card.sup_type,
            "description": card.description,
            "order": card.order
        }

    @staticmethod
    @my_require_http_methods(['GET'])
    def get_card_types(request):
        logger.info("get card types")
        cards = [Card_type.DATA, Card_type.SCENE, Card_type.VALUE, Card_type.VISION, Card_type.TOOL]
        return JsonResponse(cards, safe=False)

    @staticmethod
    @my_require_http_methods(['GET'])
    def get_cards_by_type(request, card_tpye):
        cards = Card.objects.filter(type=card_tpye).order_by('sup_type').order_by('order')
        return JsonResponse(list(map(CardService.get_card, cards)), safe=False)

    @staticmethod
    @my_require_http_methods(['GET'])
    def get_tools_cards(request):
        toolsTypes = ToolCardTypes.getMemberValues()
        conditions = map(lambda sup_type: Q(sup_type=sup_type), toolsTypes)
        condition = reduce(lambda a, b: a | b, conditions)
        cards = Card.objects.filter(condition).order_by('sup_type').order_by('order')
        return JsonResponse(list(map(CardService.get_card, cards)), safe=False)

    @staticmethod
    @my_require_http_methods(['GET'])
    def get_cards(request):
        cards = Card.objects.all().order_by('sup_type').order_by('order')
        return JsonResponse(list(map(CardService.get_card, cards)), safe=False)
