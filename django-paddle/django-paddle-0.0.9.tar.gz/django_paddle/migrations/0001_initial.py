# Generated by Django 3.0.4 on 2020-05-09 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaddlePlan',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('billing_type', models.CharField(max_length=255)),
                ('billing_period', models.PositiveIntegerField()),
                ('trial_days', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PaddleSubscription',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False, unique=True)),
                ('user_id', models.PositiveIntegerField()),
                ('user_email', models.EmailField(max_length=254)),
                ('marketing_consent', models.BooleanField()),
                ('update_url', models.CharField(max_length=255)),
                ('cancel_url', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('signup_date', models.DateTimeField()),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='django_paddle.PaddlePlan')),
            ],
        ),
        migrations.CreateModel(
            name='PaddleRecurringPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=255)),
                ('amount', models.CharField(max_length=255)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_prices', to='django_paddle.PaddlePlan')),
            ],
            options={
                'default_related_name': 'recurring_prices',
            },
        ),
        migrations.CreateModel(
            name='PaddlePayment',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False, unique=True)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=255)),
                ('payout_date', models.DateField(max_length=255)),
                ('is_paid', models.BooleanField()),
                ('is_one_off_charge', models.BooleanField()),
                ('receipt_url', models.CharField(max_length=255, null=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='django_paddle.PaddleSubscription')),
            ],
        ),
        migrations.CreateModel(
            name='PaddleInitialPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=255)),
                ('amount', models.CharField(max_length=255)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initial_prices', to='django_paddle.PaddlePlan')),
            ],
            options={
                'default_related_name': 'initial_prices',
            },
        ),
    ]
