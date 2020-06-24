import logging

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from marshmallow.exceptions import ValidationError
from functools import reduce

from workshop.enums import StepTypes, RoleTypes
from workshop.models import User, UserWorkbench, Workbench, Step
from workshop.schemas import CreateUser, LoginUser, CreateWorkbench, AddUsers, UpdateWorkbench
from workshop.decorators import login_required_401

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
    """
    Get all users except superuser and the user self
    :param request:
    :return:
    """
    users = User.objects.all()

    def get_user_data(user_list: list, user: User):
        if not user.is_superuser and user != request.user:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return user_list

    users_data = reduce(get_user_data, list(users), [])
    return JsonResponse(users_data, safe=False)


@login_required_401
@require_http_methods(['GET', 'POST'])
def users_in_workbench(request, workbench_id: int):
    """
    GET: List all users in workbench
    POST: Add users to workbench
    :param request:
    :param workbench_id:
    :return:
    """
    if request.method == 'GET':
        user_workbenches = UserWorkbench.objects.filter(workbench=workbench_id).order_by('created_at')
        creator: User = Workbench.objects.get(id=workbench_id).created_by

        def get_user_data(user_workbench: UserWorkbench):
            return {
                'username': user_workbench.user.username,
                'email': user_workbench.user.email,
                'role': RoleTypes.CREATOR if user_workbench.user == creator else RoleTypes.MEMBER
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


def index(request):
    request.META["CSRF_COOKIE_USED"] = True
    return render(request, 'index.html')
