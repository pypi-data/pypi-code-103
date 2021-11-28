# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-19 14:13
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0003_TestBuild_is_active_use_custom_bool_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testenvironmentelement",
            name="parent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="parent_set",
                to="management.TestEnvironmentElement",
            ),
        ),
    ]
