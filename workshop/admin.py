from django.contrib import admin

# Register your models here.
from .models import User, Workshop, Workbench, UserWorkbench
admin.site.register(User)
admin.site.register(Workshop)
admin.site.register(Workbench)
admin.site.register(UserWorkbench)
