from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.utils import IntegrityError
from marshmallow.exceptions import ValidationError

from .models import User, UserWorkbench
from .schemas import CreateUser, LoginUser
from .decorators import login_required_401


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
    user_workbenches = UserWorkbench.objects.filter(user_id=current_user)

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
