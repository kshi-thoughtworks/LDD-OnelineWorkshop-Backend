# Generated by Django 3.0.6 on 2020-06-23 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0017_element_version'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='sub_type',
            new_name='sup_type',
        ),
    ]