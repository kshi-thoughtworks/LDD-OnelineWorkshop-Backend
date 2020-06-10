from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from functools import reduce
from marshmallow.exceptions import ValidationError

from .models import User, Workshop, UserWorkbench
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
    except Exception as e:
        return HttpResponse(e, status=400)
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
def get_workshops_by_user(request):
    current_user = request.user
    user_workbenches = UserWorkbench.objects.filter(user_id=current_user)
    print(user_workbenches)

    def get_unique_workshop(workshop_list, user_workbench: UserWorkbench):
        workshop = Workshop.objects.get(workbench=user_workbench.workbench_id)
        workshop_ids = {item['id'] for item in workshop_list}
        if workshop.id in workshop_ids:
            return workshop_list
        else:
            return workshop_list + [
                {
                    "id": workshop.id,
                    "name": workshop.name,
                    "description": workshop.description
                }
            ]

    workshops = reduce(get_unique_workshop, [[], ] + list(user_workbenches))
    return HttpResponse(workshops)
