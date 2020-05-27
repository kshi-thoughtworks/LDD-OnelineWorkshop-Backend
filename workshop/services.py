from django.http import HttpResponse
from .models import User


def index(request):
    return HttpResponse("Hello, world. You're at the workshop index.")


def list_users(request):
    users = User.objects.all()
    return HttpResponse(users, content_type="text/plain")
