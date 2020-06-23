import logging

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from marshmallow.exceptions import ValidationError

from .enums import Card_type, StepTypes
from .models import User, UserWorkbench, Workbench, Step, Element, Card
from .schemas import CreateUser, LoginUser, CreateWorkbench, AddUsers, UpdateWorkbench, CreateSticker, CreateCard, \
    UpdateElement
from .decorators import login_required_401

UNIQUE_ERROR_PREFIX = "UNIQUE constraint failed"

logger = logging.getLogger(__name__)


def register_user(request):
    try:
        user = CreateUser.Schema().loads(request.body)
        User.objects.create_user(username=user.username, email=user.email, password=user.password)
    except IntegrityError as e:
        if str.startswith(str(e), UNIQUE_ERROR_PREFIX):
            field = str(e).split(".")[1]
            return HttpResponse(f'{field} already exists', status=400)
    except Exception as e:
        return HttpResponse(e, status=422)
    return HttpResponse()


def login_user(request):
    try:
        user_data = LoginUser.Schema().loads(request.body)
    except ValidationError as e:
        return HttpResponse(e, status=400)

    if "@" in user_data.name_or_email:
        try:
            user = User.objects.get(email=user_data.name_or_email)
        except User.DoesNotExist:
            return HttpResponse("username or password is invalid", status=401)
        username = user.username
    else:
        username = user_data.name_or_email

    auth_user = authenticate(request, username=username, password=user_data.password)
    if auth_user is not None:
        login(request, auth_user)
        data = {
            'username': auth_user.username,
            'is_coach': auth_user.is_staff
        }
        return JsonResponse(data)
    else:
        return HttpResponse("username or password is invalid", status=401)


@login_required_401
@require_http_methods(['GET'])
def list_users(request):
    users = User.objects.all()

    def get_user_data(user: User):
        return {
            'username': user.username,
            'email': user.email
        }

    users_data = list(map(get_user_data, users))
    return JsonResponse(users_data, safe=False)


@login_required_401
@require_http_methods(['GET', 'POST'])
def users_in_workbench(request, workbench_id: int):
    """
    GET: List all users in workbench
    PUT: Add users to workbench
    :param request:
    :param workbench_id:
    :return:
    """
    if request.method == 'GET':
        user_workbenches = UserWorkbench.objects.filter(workbench=workbench_id).order_by('created_at')

        def get_user_data(user_workbench: UserWorkbench):
            return {
                'username': user_workbench.user.username,
                'email': user_workbench.user.email
            }

        users_data = list(map(get_user_data, user_workbenches))
        return JsonResponse(users_data, safe=False)

    elif request.method == 'POST':
        try:
            user_ids = AddUsers.Schema().loads(request.body).user_ids
            workbench = Workbench.objects.get(id=workbench_id)
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    user_workbench = UserWorkbench(user=user, workbench=workbench)
                    user_workbench.save()
                except IntegrityError as e:
                    if str.startswith(str(e), UNIQUE_ERROR_PREFIX):
                        return HttpResponse(f'user_id {user_id} already exists in workbench_id {workbench_id}',
                                            status=400)
        except Exception as e:
            return HttpResponse(e, status=422)
        return HttpResponse()


@login_required_401
@require_http_methods(['GET', 'POST'])
def workbenches_ops(request):
    # get user's workbenches
    if request.method == 'GET':
        current_user = request.user
        user_workbenches = UserWorkbench.objects.filter(user_id=current_user.id)

        def get_workbench(user_workbench: UserWorkbench):
            workbench = user_workbench.workbench
            return {
                "id": workbench.id,
                "name": workbench.name,
                "description": workbench.description,
                "created_at": workbench.created_at.strftime("%Y-%m-%d")
            }

        workbenches = list(map(get_workbench, user_workbenches))

        return JsonResponse(workbenches, safe=False)
    # add workbench
    if request.method == 'POST':
        try:
            create_workbench = CreateWorkbench.Schema().loads(request.body)
            workbench = Workbench(name=create_workbench.name, description=create_workbench.description,
                                  created_by=User.objects.get(id=request.user.id))
            workbench.save()

            # add default step
            default_steps = [
                {
                    'type': StepTypes.DATA_PANORAMA,
                    'name': '数据全景图',
                    'order': 10
                },
                {
                    'type': StepTypes.TECHNOLOGY_CARD,
                    'name': '技术卡',
                    'order': 20
                },
                {
                    'type': StepTypes.DIVERGENCE_SCENE,
                    'name': '发散场景',
                    'order': 30
                },
                {
                    'type': StepTypes.CONVERGENCE_SCENE,
                    'name': '收敛场景',
                    'order': 40
                },
                {
                    'type': StepTypes.GENERATE_REPORT,
                    'name': '生成报告',
                    'order': 50
                }]
            for step in default_steps:
                step = Step(name=step['name'], order=step['order'], type=step['type'], workbench=workbench)
                step.save()

            # default add self in this workbench
            userWorkbench = UserWorkbench(user=request.user, workbench=workbench)
            userWorkbench.save()
            response = {
                "workbench_id": workbench.id
            }
            return JsonResponse(response)
        except ValidationError as e:
            return HttpResponse(e, status=400)
        except Exception as e:
            return HttpResponse(e, status=500)


@login_required_401
@require_http_methods(['GET', 'PUT'])
def workbenches_ops_by_id(request, workbench_id):
    """
    GET: get workbench by id
    PUT: update workbench by id
    :param request:
    :param workbench_id:
    :return:
    """
    try:
        if request.method == 'GET':
            workbench = Workbench.objects.get(id=workbench_id)
            steps = Step.objects.filter(workbench_id=workbench_id).order_by('order')

            # steps = serializers.serialize('json', steps)
            def get_step(step: Step):
                return {
                    "id": step.id,
                    "name": step.name,
                    "order": step.order,
                    "type": step.type
                }

            data = {
                'id': workbench.id,
                'name': workbench.name,
                'description': workbench.description,
                'created_by': workbench.created_by.username,
                'created_at': workbench.created_at,
                'steps': list(map(get_step, steps))
            }
            return JsonResponse(data, safe=False)
        if request.method == 'PUT':
            user = request.user
            updateWorkbench = UpdateWorkbench.Schema().loads(request.body)
            workbench = Workbench.objects.get(pk=workbench_id)
            if workbench.created_by.id != user.id:
                return HttpResponse('you don\'t onw this workbench', status=403)
            if updateWorkbench.name.strip(' ') is not None:
                workbench.name = updateWorkbench.name.strip(' ')
            if updateWorkbench.description.strip(' ') is not None:
                workbench.description = updateWorkbench.description.strip(' ')
            workbench.save()
            return HttpResponse()
    except ValidationError as e:
        return HttpResponse(e, status=400)


def elements_ops(request, createElement):
    try:
        createElement = createElement.Schema().loads(request.body)
        element = Element(type=createElement.type,
                          content=createElement.content,
                          title=createElement.title,
                          step=Step.objects.get(pk=createElement.step_id),
                          created_by=request.user,
                          meta=createElement.meta)
        if createElement.card_id is not None:
            element.card = Card.objects.get(pk=createElement.card_id)
        element.save()
        response = {
            "element_id": element.id
        }
        return JsonResponse(response)
    except ValidationError as e:
        print(e)
        return HttpResponse(e, status=400)
    except Exception as e:
        print(e)
        return HttpResponse(e, status=500)


@login_required_401
@require_http_methods(['POST'])
def elements_stickers_ops(request):
    return elements_ops(request, CreateSticker)


@login_required_401
@require_http_methods(['POST'])
def elements_cards_ops(request):
    return elements_ops(request, CreateCard)


@login_required_401
@require_http_methods(['POST'])
def copy_element_by_id(request, element_id):
    try:
        oldElement = Element.objects.get(pk=element_id)

        element = Element(type=oldElement.type,
                          content=oldElement.content,
                          step=Step.objects.get(pk=oldElement.step_id),
                          created_by=request.user
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
            'created_by': element.created_by.id
        }
        return JsonResponse(response)
    except Exception as e:
        return HttpResponse(e, status=500)


@login_required_401
@require_http_methods(['GET', 'PUT', 'DELETE'])
def elements_ops_by_id(request, element_id):
    try:
        element = Element.objects.get(pk=element_id)
        if request.method == 'GET':
            return get_element_by_id(element)
        if request.method == 'PUT':
            return update_element_by_id(element, request)
        if request.method == 'DELETE':
            return delete_element_by_id(element)
    except ValidationError as e:
        return HttpResponse(e, status=400)


def get_element_by_id(element):
    return JsonResponse({
        'type': element.type,
        'title': element.title,
        'content': element.content,
        'step_id': element.step.id,
        'card': element.card.name if element.card is not None else '',
        'meta': element.meta,
        'created_by': element.created_by.id})


def update_element_by_id(element, request):
    update_element = UpdateElement.Schema().loads(request.body)
    if update_element.title.strip(' ') is not None:
        element.title = update_element.title.strip(' ')
    if update_element.content.strip(' ') is not None:
        element.content = update_element.content.strip(' ')
    if update_element.meta is not None:
        element.meta = update_element.meta
    element.save()
    return HttpResponse()


def delete_element_by_id(element):
    if element is not None:
        element.delete()
    return HttpResponse()


@login_required_401
@require_http_methods(['GET'])
def list_elements_by_step(request, step_id):
    elements = Element.objects.filter(step_id=step_id)

    def get_card(card: Card):
        if card is not None:
            return {
                "id": card.id,
                "name": card.name,
                "type": card.type,
                "description": card.description,
                "order": card.order
            }
        else:
            return None

    def get_element_data(element: Element):
        data = {
            'id': element.id,
            'type': element.type,
            'title': element.title,
            'content': element.content,
            'step_id': element.step.id,
            'meta': element.meta,
            'created_by': element.created_by.id
        }
        if element.card is not None:
            data['card'] = get_card(element.card)
        return data

    elements_data = list(map(get_element_data, elements))
    return JsonResponse(elements_data, safe=False)


@login_required_401
@require_http_methods(['GET'])
def get_card_types(request):
    logger.info("get card types")
    cards = [Card_type.DATA, Card_type.SCENE, Card_type.VALUE, Card_type.VISION, Card_type.TOOL]
    return JsonResponse(cards, safe=False)


@login_required_401
@require_http_methods(['GET'])
def get_cards_by_type(request, card_tpye):
    cards = Card.objects.filter(type=card_tpye).order_by('sub_type').order_by('order')

    def get_card(card: Card):
        return {
            "id": card.id,
            "name": card.name,
            "type": card.type,
            "sub_type": card.sub_type,
            "description": card.description,
            "order": card.order
        }

    return JsonResponse(list(map(get_card, cards)), safe=False)


@login_required_401
@require_http_methods(['GET'])
def get_cards(request):
    cards = Card.objects.all().order_by('sub_type').order_by('order')

    def get_card(card: Card):
        return {
            "id": card.id,
            "name": card.name,
            "type": card.type,
            "sub_type": card.sub_type,
            "description": card.description,
            "order": card.order
        }

    return JsonResponse(list(map(get_card, cards)), safe=False)


def index(request):
    request.META["CSRF_COOKIE_USED"] = True
    return render(request, 'index.html')
