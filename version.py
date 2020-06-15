import subprocess
from django.http import JsonResponse

from server.settings import BASE_DIR


def get_version(request):
    out_bytes = subprocess.check_output(['cat', BASE_DIR + '/version'])
    out_text = out_bytes.decode('utf-8')
    data = {
        "version": out_text
    }
    return JsonResponse(data)

