# Generated by Django 1.11.10 on 2018-02-23 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0015_user_profiles'),
        ('teamspeak3', '0004_service_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.State')),
                ('ts_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamspeak3.TSgroup')),
            ],
        ),
    ]
