# Generated by Django 3.0.6 on 2020-06-22 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0014_step_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='title',
            field=models.CharField(default='', max_length=1024),
        ),
    ]
