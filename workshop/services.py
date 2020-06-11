from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from marshmallow.exceptions import ValidationError

from .models import User, UserWorkbench, Workbench, Workshop
from .schemas import CreateUser, LoginUser, CreateWorkbench, AddUserToWorkbench
from .decorators import login_required_401, http_method


def register_user(request):
    try:
        user = CreateUser.Schema().loads(request.body)
        User.objects.create_user(username=user.username, email=user.email, password=user.password)
    except IntegrityError as e:
        if str.startswith(str(e), "UNIQUE constraint failed"):
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
def list_users_by_workbench(request, workbench_id: int):
    user_workbenches = UserWorkbench.objects.filter(workbench=workbench_id)

    def get_user_data(user_workbench: UserWorkbench):
        return {
            'username': user_workbench.user.username,
            'email': user_workbench.user.email
        }
    users_data = list(map(get_user_data, user_workbenches))
    return JsonResponse(users_data, safe=False)


@login_required_401
def list_workbenches_by_user(request):
    current_user = request.user
    user_workbenches = UserWorkbench.objects.filter(user_id=current_user)

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


@login_required_401
def create_workbench(request):
    try:
        create_workbench = CreateWorkbench.Schema().loads(request.body)
        workbench = Workbench(name=create_workbench.name, description=create_workbench.description,
                              workshop=Workshop.objects.get(id=create_workbench.workshop_id),
                              created_by=request.user)
        workbench.save()
        return HttpResponse()
    except ValidationError as e:
        return HttpResponse(e, status=400)
    except Exception as e:
        return HttpResponse(e, status=500)


@login_required_401
@http_method('GET')
def get_workbench_by_id(request, workbench_id):
    try:
        workbench = Workbench.objects.get(id=workbench_id)
        data = {
            'name': workbench.name,
            'description': workbench.description,
            'workshop_id': workbench.workshop.id,
            'created_by': workbench.created_by,
            'created_at': workbench.created_at
        }
        return JsonResponse(data)
    except ValidationError as e:
        return HttpResponse(e, status=400)


@login_required_401
def add_user_to_workbench(request):
    try:
        data = AddUserToWorkbench.Schema().loads(request.body)
        workbench = Workbench.objects.get(id=data.workbench_id)
        user = User.objects.get(id=data.user_id)
        user_workbench = UserWorkbench(user=user, workbench=workbench)
        user_workbench.save()
    except Exception as e:
        return HttpResponse(e, status=422)
    return HttpResponse()
