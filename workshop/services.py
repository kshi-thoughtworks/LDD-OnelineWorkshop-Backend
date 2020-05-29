import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User


def index(request):
    return HttpResponse("Hello, world. You're at the workshop index.")


def list_users(request):
    users = User.objects.all()
    return HttpResponse(users, content_type="text/plain")


@csrf_exempt
def register_user(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')
    password = data.get('password', '')
    User.objects.create_user(username=username, password=password)
    return HttpResponse()
