# Generated by Django 3.0.6 on 2020-06-22 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0015_element_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='sup_type',
            new_name='sub_type',
        ),
    ]
