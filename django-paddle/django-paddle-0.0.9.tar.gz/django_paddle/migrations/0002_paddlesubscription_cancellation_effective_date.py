# Generated by Django 3.2.4 on 2021-11-28 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_paddle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paddlesubscription',
            name='cancellation_effective_date',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
