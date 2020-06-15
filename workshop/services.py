from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from marshmallow.exceptions import ValidationError

from .models import User, UserWorkbench, Workbench, Workshop
from .schemas import CreateUser, LoginUser, CreateWorkbench
from .decorators import login_required_401, http_method


@login_required_401
def list_users(request):
    users = User.objects.all()
    return HttpResponse(users, content_type="text/plain")


@csrf_exempt
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


@csrf_exempt
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
def get_workbenches_by_user(request):
    current_user = request.user
    user_workbenches = UserWorkbench.objects.filter(user_id=current_user.id)

    def get_workbench(user_workbench: UserWorkbench):
        workbench = user_workbench.workbench
        return {
            "id": workbench.id,
            "name": workbench.name,
            "description": workbench.description,
            "created_at": workbench.created_at
        }

    workbenches = map(get_workbench, user_workbenches)

    return HttpResponse(workbenches)


@csrf_exempt
@login_required_401
@http_method('POST')
def create_workbench(request):
    try:
        create_workbench = CreateWorkbench.Schema().loads(request.body)
        workbench = Workbench(name=create_workbench.name, description=create_workbench.description,
                              workshop=Workshop.objects.get(id=create_workbench.workshop_id),
                              created_by=User.objects.get(id=request.user.id))
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
            'created_by': workbench.created_by.username,
            'created_at': workbench.created_at
        }
        return JsonResponse(data)
    except ValidationError as e:
        return HttpResponse(e, status=400)


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
