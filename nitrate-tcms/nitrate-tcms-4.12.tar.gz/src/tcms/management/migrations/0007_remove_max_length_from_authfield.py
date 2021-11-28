# Generated by Django 3.0.7 on 2020-06-24 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0006_auto_20190525_1454"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="priority",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="product",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="testattachment",
            name="attachment_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="testbuild",
            name="build_id",
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name="testenvironment",
            name="environment_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="testenvironmentelement",
            name="element_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="testtag",
            name="id",
            field=models.AutoField(db_column="tag_id", primary_key=True, serialize=False),
        ),
    ]
