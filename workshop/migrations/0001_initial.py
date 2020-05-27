# Generated by Django 3.0.6 on 2020-05-27 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50, null=True)),
                ('wechat_id', models.IntegerField(null=True)),
                ('type', models.CharField(max_length=20, null=True)),
                ('organization', models.CharField(max_length=100, null=True)),
                ('phone', models.IntegerField(null=True)),
                ('position', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]
