# Generated by Django 2.0.4 on 2018-05-06 21:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('Austria', 'Austria'), ('England', 'England'), ('France', 'France'), ('Germany', 'Germany'), ('Italy', 'Italy'), ('Russia', 'Russia'), ('Turkey', 'Turkey')], max_length=7)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('players', models.ManyToManyField(related_name='games', through='game.Country', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order_type', models.CharField(choices=[('hold', 'hold'), ('move', 'move'), ('support', 'support'), ('convoy', 'convoy'), ('create', 'create')], max_length=7)),
                ('coast', models.CharField(blank=True, choices=[('NC', 'north'), ('EC', 'east'), ('SC', 'south')], max_length=2)),
                ('aux_order_type', models.CharField(blank=True, choices=[('hold', 'hold'), ('move', 'move')], max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('via_convoy', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Territory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('abbreviation', models.CharField(max_length=3)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='territories', to='game.Game')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='territories', to='game.Country')),
            ],
            options={
                'verbose_name_plural': 'territories',
            },
        ),
        migrations.CreateModel(
            name='Turn',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('year', models.PositiveSmallIntegerField(default=1901)),
                ('season', models.CharField(choices=[('spring', 'spring'), ('fall', 'fall')], max_length=6)),
                ('phase', models.CharField(choices=[('diplomatic', 'diplomatic'), ('retreat', 'retreat'), ('reinforcement', 'reinforcement')], max_length=13)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turns', to='game.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('unit_type', models.CharField(choices=[('army', 'army'), ('fleet', 'fleet')], max_length=5)),
                ('coast', models.CharField(blank=True, choices=[('NC', 'north'), ('EC', 'east'), ('SC', 'south')], max_length=2)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='units', to='game.Country')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='units', to='game.Game')),
                ('invaded_from', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Territory')),
                ('retreating_from', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retreating_unit', to='game.Territory')),
                ('territory', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.Territory')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='aux_destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Territory'),
        ),
        migrations.AddField(
            model_name='order',
            name='aux_origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Territory'),
        ),
        migrations.AddField(
            model_name='order',
            name='aux_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Unit'),
        ),
        migrations.AddField(
            model_name='order',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Territory'),
        ),
        migrations.AddField(
            model_name='order',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Territory'),
        ),
        migrations.AddField(
            model_name='order',
            name='turn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='game.Turn'),
        ),
        migrations.AddField(
            model_name='order',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='game.Unit'),
        ),
        migrations.AddField(
            model_name='country',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='countries', to='game.Game'),
        ),
        migrations.AddField(
            model_name='country',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='countries', to=settings.AUTH_USER_MODEL),
        ),
    ]
