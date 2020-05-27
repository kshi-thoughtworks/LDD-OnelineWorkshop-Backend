from django.db import models


class User(models.Model):
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50, null=True)
    wechat_id = models.IntegerField(null=True)
    type = models.CharField(max_length=20, null=True)
    organization = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(null=True)
    position = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name
