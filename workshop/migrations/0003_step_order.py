# Generated by Django 3.0.6 on 2020-06-02 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0002_auto_20200602_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
