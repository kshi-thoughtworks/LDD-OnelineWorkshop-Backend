# Generated by Django 3.0.6 on 2020-06-18 12:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0013_update_matrix_to_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='type',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
