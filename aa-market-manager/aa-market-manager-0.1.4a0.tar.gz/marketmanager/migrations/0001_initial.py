# Generated by Django 3.2.8 on 2021-11-26 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('eveuniverse', '0005_type_materials_and_sections'),
        ('eveonline', '0015_factions'),
    ]

    operations = [
        migrations.CreateModel(
            name='General',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('basic_access', 'Can access this app'),),
                'managed': False,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('structure_id', models.PositiveBigIntegerField(primary_key=True, serialize=False, verbose_name='Structure ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('owner_id', models.IntegerField(verbose_name='Owner ID')),
                ('pull_market', models.BooleanField(default=True, help_text='Useful to ignore specific structures for _reasons_', verbose_name='Pull Market Orders')),
                ('eve_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eveuniverse.evetype', verbose_name='')),
                ('solar_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eveuniverse.evesolarsystem', verbose_name='Solar System')),
            ],
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('webhook', models.URLField(verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='WatchConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy_order', models.BooleanField(verbose_name='Buy Order')),
                ('volume', models.IntegerField(help_text='Set to Zero to check ANY/EVERY order against Price', verbose_name='Volume')),
                ('price', models.IntegerField(help_text='Set to Zero to check ANY/EVERY order against Volume', verbose_name='Price')),
                ('jita_compare_percent', models.IntegerField(help_text='If set ignores Flat price value', verbose_name='Jita Comparison %')),
                ('constellation', models.ManyToManyField(to='eveuniverse.EveConstellation', verbose_name='')),
                ('location', models.ManyToManyField(to='marketmanager.Structure', verbose_name='')),
                ('region', models.ManyToManyField(to='eveuniverse.EveRegion', verbose_name='')),
                ('solar_system', models.ManyToManyField(to='eveuniverse.EveSolarSystem', verbose_name='')),
                ('structure_type', models.ManyToManyField(help_text='Filter by structure Type/Size/Docking (ie, forts/keeps for cap fuel)', related_name='structure_type', to='eveuniverse.EveType', verbose_name='Structure Type Filter')),
                ('type', models.ManyToManyField(to='eveuniverse.EveType', verbose_name='EVE Types')),
                ('webhooks', models.ManyToManyField(to='marketmanager.Webhook', verbose_name='Webhooks')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.PositiveBigIntegerField(help_text='Unique order ID', primary_key=True, serialize=False, verbose_name='Order ID')),
                ('duration', models.PositiveIntegerField(help_text='Number of days the order was valid for (starting from the issued date). An order expires at time issued + duration', verbose_name='Duration')),
                ('is_buy_order', models.BooleanField(default=False, help_text='True if the order is a bid (buy) order', verbose_name='Buy Order')),
                ('issued', models.DateTimeField(help_text='Date and time when this order was issued', verbose_name='Issued')),
                ('location_id', models.PositiveBigIntegerField(help_text='ID of the location where order was placed', verbose_name='Location ID')),
                ('min_volume', models.PositiveIntegerField(blank=True, help_text='For buy orders, the minimum quantity that will be accepted in a matching sell order', null=True, verbose_name='Minimum Volume')),
                ('price', models.DecimalField(decimal_places=2, help_text='Cost per unit for this order', max_digits=20, verbose_name='Price')),
                ('escrow', models.DecimalField(blank=True, decimal_places=2, help_text='For buy orders, the amount of ISK in escrow', max_digits=20, null=True, verbose_name='Escrow')),
                ('range', models.CharField(choices=[('1', '1'), ('10', '10'), ('2', '2'), ('20', '20'), ('3', '3'), ('30', '30'), ('4', '4'), ('40', '40'), ('5', '5'), ('region', 'Region'), ('solarsystem', 'Solar System'), ('station', 'Station')], help_text='Valid order range, numbers are ranges in jumps', max_length=20, verbose_name='Order Range')),
                ('volume_remain', models.PositiveIntegerField(help_text='Quantity of items still required or offered', verbose_name='Volume Remaining')),
                ('volume_total', models.PositiveIntegerField(help_text='Quantity of items required or offered at time order was placed', verbose_name='Volume Total')),
                ('is_corporation', models.BooleanField(default=False, help_text='Signifies whether the buy/sell order was placed on behalf of a corporation.', verbose_name='Is Corporation')),
                ('wallet_division', models.PositiveIntegerField(blank=True, help_text='The corporation wallet division used for this order.', null=True, verbose_name='Wallet Division')),
                ('state', models.CharField(choices=[('1', '1'), ('10', '10'), ('2', '2'), ('20', '20'), ('3', '3'), ('30', '30'), ('4', '4'), ('40', '40'), ('5', '5'), ('region', 'Region'), ('solarsystem', 'Solar System'), ('station', 'Station')], help_text='Current order state, Only valid for Authenticated order History. Will not update from Public Market Data.', max_length=20, verbose_name='Order State')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('eve_region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eveuniverse.everegion', verbose_name='Region')),
                ('eve_solar_system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eveuniverse.evesolarsystem', verbose_name='System')),
                ('eve_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eveuniverse.evetype', verbose_name='Type')),
                ('issued_by_character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='eveonline.evecharacter', verbose_name='Character')),
                ('issued_by_corporation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='eveonline.evecorporationinfo', verbose_name='Corporation')),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fetch_regions', models.ManyToManyField(to='eveuniverse.EveRegion', verbose_name='Fetch Regions')),
            ],
        ),
    ]
