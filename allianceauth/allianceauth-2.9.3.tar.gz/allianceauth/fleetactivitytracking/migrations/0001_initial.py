# Generated by Django 1.10.1 on 2016-09-05 21:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone

import allianceauth.fleetactivitytracking.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eveonline', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system', models.CharField(max_length=30)),
                ('shiptype', models.CharField(max_length=30)),
                ('station', models.CharField(max_length=125)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eveonline.EveCharacter')),
            ],
        ),
        migrations.CreateModel(
            name='Fatlink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fatdatetime', models.DateTimeField(default=timezone.now)),
                ('duration', models.PositiveIntegerField()),
                ('fleet', models.CharField(default='', max_length=254)),
                ('name', models.CharField(max_length=254)),
                ('hash', models.CharField(max_length=254, unique=True)),
                ('creator', models.ForeignKey(on_delete=models.SET(
                    allianceauth.fleetactivitytracking.models.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='fat',
            name='fatlink',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleetactivitytracking.Fatlink'),
        ),
        migrations.AddField(
            model_name='fat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='fat',
            unique_together={('character', 'fatlink')},
        ),
    ]
