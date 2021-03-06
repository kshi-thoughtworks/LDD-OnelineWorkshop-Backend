import json
from django.db import models
from django.contrib.auth.models import AbstractUser

from workshop.enums import Element_type


class JSONField(models.TextField):
    description = "Json"

    def to_python(self, value):
        v = models.TextField.to_python(self, value)
        try:
            return json.loads(v)
        except:
            pass
        return v

    def get_prep_value(self, value):
        if type(value) is dict:
            return json.dumps(value, ensure_ascii=False)
        else:
            return value


class User(AbstractUser):
    email = models.CharField(unique=True, max_length=100, verbose_name='email address')
    type = models.CharField(max_length=20, null=True)
    organization = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(null=True)
    position = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.username


class Workbench(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserWorkbench(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workbench = models.ForeignKey(Workbench, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'workbench'], name='unique_assign')
        ]

    def __str__(self):
        return f'{self.workbench.name} : {self.user.username}'


class Card(models.Model):
    name = models.CharField(max_length=100)
    # 当前卡的类型
    type = models.CharField(max_length=20)
    # 父类卡的类型
    sup_type = models.CharField(max_length=20, default='')
    description = JSONField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Step(models.Model):
    name = models.CharField(max_length=100)
    workbench = models.ForeignKey(Workbench, on_delete=models.CASCADE)
    order = models.IntegerField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Element(models.Model):
    type = models.CharField(max_length=20, default=Element_type.STICKY)
    title = models.CharField(max_length=1024, default='')
    content = JSONField()
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    version = models.IntegerField(default=0)
    # save properties, such as: x, y, height, width, rotate, scale, color, length
    meta = JSONField(max_length=1024, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ref_element = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content
