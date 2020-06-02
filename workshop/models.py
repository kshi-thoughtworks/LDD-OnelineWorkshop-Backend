from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    wechat_id = models.IntegerField(null=True)
    type = models.CharField(max_length=20, null=True)
    organization = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(null=True)
    position = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.username


class Workshop(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Workbench(models.Model):
    name = models.CharField(max_length=100)
    workshop_id = models.ForeignKey(Workshop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserWorkbench(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    workbench_id = models.ForeignKey(Workbench, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.workbench_id.name} : {self.user_id.username}'
