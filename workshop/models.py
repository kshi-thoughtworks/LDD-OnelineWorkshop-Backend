from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.CharField(unique=True, max_length=100, verbose_name='email address')
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
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserWorkbench(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workbench = models.ForeignKey(Workbench, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.workbench.name} : {self.user.username}'


class Card(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    description = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


class Step(models.Model):
    name = models.CharField(max_length=100)
    workbench = models.ForeignKey(Workbench, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return self.name


class Sticker(models.Model):
    type = models.CharField(max_length=20)
    content = models.CharField(max_length=1024)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.content
