# Generated by Django 1.10.1 on 2016-09-05 22:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fleetactivitytracking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatlink',
            name='fatdatetime',
            field=models.DateTimeField(default=datetime.datetime(2016, 9, 5, 22, 20, 2, 999041, tzinfo=utc)),
        ),
    ]
