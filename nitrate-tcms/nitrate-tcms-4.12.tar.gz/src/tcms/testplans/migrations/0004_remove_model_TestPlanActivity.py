# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-10 11:36
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("testplans", "0003_remove_model_TestPlanPermission"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="testplanactivity",
            name="plan",
        ),
        migrations.RemoveField(
            model_name="testplanactivity",
            name="who",
        ),
        migrations.DeleteModel(
            name="TestPlanActivity",
        ),
    ]
