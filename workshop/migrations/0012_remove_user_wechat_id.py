# Generated by Django 3.0.6 on 2020-06-17 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0011_card_sup_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='wechat_id',
        ),
    ]
