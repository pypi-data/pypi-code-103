# Generated by Django 3.1.2 on 2020-10-20 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0082_auto_20201020_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketUDFTracker',
            fields=[
            ],
            options={
                'db_table': 'djautotask_ticketudf',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('djautotask.ticketudf',),
        ),
    ]
