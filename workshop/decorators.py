from django.http import HttpResponse


def login_required_401(function=None):
    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse(status=401)
        return _wrapped_view

    if function is None:
        return _decorator
    else:
        return _decorator(function)


def http_method(permit_methods=None, function=None):
    if permit_methods is None:
        permit_methods = []

    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.method in permit_methods:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("http method not support", status=405)
        return _wrapped_view

    if function is None:
        return _decorator
    else:
        return _decorator(function)
