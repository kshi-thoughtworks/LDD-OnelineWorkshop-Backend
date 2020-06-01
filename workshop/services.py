import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.http import JsonResponse

from .models import User


def index(request):
    return HttpResponse("Hello, world. You're at the workshop index.")


@login_required
def list_users(request):
    users = User.objects.all()
    return HttpResponse(users, content_type="text/plain")


@csrf_exempt
def register_user(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')
    password = data.get('password', '')
    try:
        User.objects.create_user(username=username, password=password)
    except ValueError as e:
        return HttpResponse(e, status=400)
    except IntegrityError as e:
        return HttpResponse(e, status=400)
    return HttpResponse()


@csrf_exempt
def login_user(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')
    password = data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        data = {
            'username': user.username,
            'is_coach': user.is_staff
        }
        return JsonResponse(data)
    else:
        return HttpResponse(status=401)
