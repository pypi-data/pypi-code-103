# Generated by Django 3.1.5 on 2021-06-04 11:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0002_auto_20210604_1545'),
        ('stick_protocol', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signedprekey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signedPreKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='prekey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pendingkey',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pendingKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pendingkey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sentPendingKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='party',
            name='connections',
            field=models.ManyToManyField(blank=True, related_name='party_connections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='party',
            name='groups',
            field=models.ManyToManyField(blank=True, to='groups.Group'),
        ),
        migrations.AddField(
            model_name='party',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parties', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='identitykey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identityKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='encryptingsenderkey',
            name='identityKey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='esk_ik', to='stick_protocol.identitykey'),
        ),
        migrations.AddField(
            model_name='encryptingsenderkey',
            name='preKey',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='esk_pk', to='stick_protocol.prekey'),
        ),
        migrations.AddField(
            model_name='encryptingsenderkey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encryptingSenderKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='decryptingsenderkey',
            name='forUser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receivedSenderKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='decryptingsenderkey',
            name='identityKey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dsk_ik', to='stick_protocol.identitykey'),
        ),
        migrations.AddField(
            model_name='decryptingsenderkey',
            name='ofUser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decryptingSenderKeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='decryptingsenderkey',
            name='preKey',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dsk_pk', to='stick_protocol.prekey'),
        ),
        migrations.AddConstraint(
            model_name='signedprekey',
            constraint=models.UniqueConstraint(fields=('keyId', 'user'), name='unique_signed_prekey'),
        ),
        migrations.AddConstraint(
            model_name='prekey',
            constraint=models.UniqueConstraint(fields=('keyId', 'user'), name='unique_prekey'),
        ),
        migrations.AddConstraint(
            model_name='identitykey',
            constraint=models.UniqueConstraint(fields=('keyId', 'user'), name='unique_identity_key'),
        ),
        migrations.AddConstraint(
            model_name='encryptingsenderkey',
            constraint=models.UniqueConstraint(fields=('partyId', 'chainId', 'user'), name='unique_esk'),
        ),
    ]
