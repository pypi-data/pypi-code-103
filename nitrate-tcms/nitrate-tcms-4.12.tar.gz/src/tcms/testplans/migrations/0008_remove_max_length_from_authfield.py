# Generated by Django 3.0.7 on 2020-06-24 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("testplans", "0007_migration_due_to_add_related_name_to_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testplan",
            name="plan_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
