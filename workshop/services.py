from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from marshmallow.exceptions import ValidationError

from .models import User, UserWorkbench, Workbench, Step
from .schemas import CreateUser, LoginUser, CreateWorkbench, AddUsers, UpdateWorkbench
from .decorators import login_required_401, http_method

UNIQUE_ERROR_PREFIX = "UNIQUE constraint failed"


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
@http_method(['GET', 'POST'])
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


@require_GET
@login_required_401
def list_workbenches_by_user(request):
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


@require_POST
@login_required_401
def create_workbench(request):
    try:
        create_workbench = CreateWorkbench.Schema().loads(request.body)
        workbench = Workbench(name=create_workbench.name, description=create_workbench.description,
                              created_by=User.objects.get(id=request.user.id))
        workbench.save()
        default_steps = {'数据全景图': 10, '技术卡': 20, '发散场景': 30, '收敛场景': 40, '生成报告': 50}
        for key, value in default_steps.items():
            step = Step(name=key, order=value, workbench=workbench)
            step.save()

        return HttpResponse()
    except ValidationError as e:
        return HttpResponse(e, status=400)
    except Exception as e:
        return HttpResponse(e, status=500)


@login_required_401
def workbench_ops(request, workbench_id):
    '''
    GET: get workbench by id
    POST: update workbench by id
    :param request:
    :param workbench_id:
    :return:
    '''
    try:
        if request.method == 'GET':
            workbench = Workbench.objects.get(id=workbench_id)
            steps = Step.objects.filter(workbench_id=workbench_id).order_by('order')
            steps = serializers.serialize('json', steps)
            data = {
                'name': workbench.name,
                'description': workbench.description,
                'created_by': workbench.created_by.username,
                'created_at': workbench.created_at,
                'steps': steps
            }
            return JsonResponse(data)
        if request.method == 'POST':
            user = request.user
            updateWorkbench = UpdateWorkbench.Schema().loads(request.body)
            workbench = Workbench.objects.get(pk=workbench_id)
            if workbench.created_by.id != user.id:
                return HttpResponse('you don\'t onw this workbench', status=403)
            if updateWorkbench.name.strip(' ') is not None:
                workbench.name = updateWorkbench.name.strip(' ')
            if updateWorkbench.description.strip(' ') is not None:
                workbench.description = updateWorkbench.name.strip(' ')
            workbench.save()
            return HttpResponse()
    except ValidationError as e:
        return HttpResponse(e, status=400)


@require_GET
@login_required_401
def get_workbench_users(request, workbench_id):
    try:
        user_workbenches = UserWorkbench.objects.filter(workbench_id=workbench_id).order_by('created_at')

        def get_user(user_workbench: UserWorkbench):
            user = user_workbench.user
            return {
                "id": user.id,
                "username": user.username,
                "description": user.email,
                "created_at": user_workbench.created_at
            }

        users = map(get_user, user_workbenches)
        return HttpResponse(users)
    except ValidationError as e:
        return HttpResponse(e, status=400)


def index(request):
    request.META["CSRF_COOKIE_USED"] = True
    return render(request, 'index.html')
