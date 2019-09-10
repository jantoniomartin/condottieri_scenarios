# -*- coding: utf-8 -*-


from django.db import models, migrations
import condottieri_scenarios.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AFToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_en', models.CharField(max_length=25, null=True, verbose_name='name', blank=True)),
                ('name_es', models.CharField(max_length=25, null=True, verbose_name='name', blank=True)),
                ('name_ca', models.CharField(max_length=25, null=True, verbose_name='name', blank=True)),
                ('name_de', models.CharField(max_length=25, null=True, verbose_name='name', blank=True)),
                ('code', models.CharField(help_text='1-5 uppercase characters to identify the area', max_length=5, verbose_name='code')),
                ('is_sea', models.BooleanField(default=False, help_text='if checked, the area is a sea, and cannot be controlled', verbose_name='is sea')),
                ('is_coast', models.BooleanField(default=False, verbose_name='is coast')),
                ('has_city', models.BooleanField(default=False, verbose_name='has city')),
                ('is_fortified', models.BooleanField(default=False, help_text='check only if the area has a city and is fortified', verbose_name='is fortified')),
                ('has_port', models.BooleanField(default=False, help_text='check only if the area has a city and a port', verbose_name='has port')),
                ('control_income', models.PositiveIntegerField(default=0, help_text='the money that a country gets for controlling both the province and the city', verbose_name='control income')),
                ('garrison_income', models.PositiveIntegerField(default=0, help_text='the money that a country gets if it has a garrison, but does not control the province', verbose_name='garrison income')),
                ('mixed', models.BooleanField(default=False, help_text='the province is a sea that can be controlled, and cannot hold an army')),
            ],
            options={
                'ordering': ('setting', 'code'),
                'verbose_name': 'area',
                'verbose_name_plural': 'areas',
            },
        ),
        migrations.CreateModel(
            name='Border',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('only_land', models.BooleanField(default=False)),
                ('from_area', models.ForeignKey(related_name='from_borders', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
                ('to_area', models.ForeignKey(related_name='to_borders', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'border',
                'verbose_name_plural': 'borders',
            },
        ),
        migrations.CreateModel(
            name='CityIncome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.ForeignKey(verbose_name='city', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'city income',
                'verbose_name_plural': 'city incomes',
            },
        ),
        migrations.CreateModel(
            name='CityRandomIncome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('income_list', models.CharField(max_length=20, verbose_name='income list', validators=[django.core.validators.RegexValidator(regex=b'^([0-9]+,\\s*){5}[0-9]+$', message='List must have 6 comma separated numbers')])),
                ('city', models.OneToOneField(verbose_name='city', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'city random income',
                'verbose_name_plural': 'cities random incomes',
            },
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('religious_war', models.BooleanField(default=False, verbose_name='religious war')),
                ('trade_routes', models.BooleanField(default=False, verbose_name='trade routes')),
            ],
        ),
        migrations.CreateModel(
            name='Contender',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.PositiveIntegerField(default=0, verbose_name='priority')),
            ],
            options={
                'ordering': ['scenario__id', 'country'],
                'verbose_name': 'contender',
                'verbose_name_plural': 'contenders',
            },
        ),
        migrations.CreateModel(
            name='ControlToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
                ('area', models.OneToOneField(to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_es', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_ca', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_de', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('color', models.CharField(help_text='Hexadecimal RGB color (e.g: FF0000 for pure red)', max_length=6, verbose_name='color')),
                ('coat_of_arms', models.ImageField(help_text='Please, use only 40x40px PNG images with transparency', upload_to=condottieri_scenarios.models.get_coat_upload_path, verbose_name='coat of arms')),
                ('can_excommunicate', models.BooleanField(default=False, verbose_name='can excommunicate')),
                ('static_name', models.SlugField(unique=True, max_length=20, verbose_name='static name')),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('protected', models.BooleanField(default=False, verbose_name='protected')),
                ('editor', models.ForeignKey(verbose_name='editor', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['static_name'],
                'verbose_name': 'country',
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='CountryRandomIncome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('income_list', models.CharField(max_length=20, verbose_name='income list', validators=[django.core.validators.RegexValidator(regex=b'^([0-9]+,\\s*){5}[0-9]+$', message='List must have 6 comma separated numbers')])),
                ('country', models.ForeignKey(verbose_name='country', to='condottieri_scenarios.Country', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'country random income',
                'verbose_name_plural': 'countries random incomes',
            },
        ),
        migrations.CreateModel(
            name='DisabledArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', models.ForeignKey(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'disabled area',
                'verbose_name_plural': 'disabled areas',
            },
        ),
        migrations.CreateModel(
            name='FamineCell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row', models.PositiveIntegerField(verbose_name='row')),
                ('column', models.PositiveIntegerField(verbose_name='column')),
                ('area', models.OneToOneField(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'famine cell',
                'verbose_name_plural': 'famine cells',
            },
        ),
        migrations.CreateModel(
            name='GToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
                ('area', models.OneToOneField(to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_home', models.BooleanField(default=True, verbose_name='is home')),
                ('area', models.ForeignKey(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
                ('contender', models.ForeignKey(verbose_name='contender', to='condottieri_scenarios.Contender', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'home area',
                'verbose_name_plural': 'home areas',
            },
        ),
        migrations.CreateModel(
            name='PlagueCell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row', models.PositiveIntegerField(verbose_name='row')),
                ('column', models.PositiveIntegerField(verbose_name='column')),
                ('area', models.OneToOneField(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'plague cell',
                'verbose_name_plural': 'plague cells',
            },
        ),
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=20, verbose_name='slug')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_es', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_ca', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
                ('name_de', models.CharField(max_length=50, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'verbose_name': 'religion',
                'verbose_name_plural': 'religions',
            },
        ),
        migrations.CreateModel(
            name='RouteStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_end', models.BooleanField(default=False)),
                ('area', models.ForeignKey(to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'route step',
                'verbose_name_plural': 'route steps',
            },
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True, max_length=128, verbose_name='slug')),
                ('title_en', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_es', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_ca', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_de', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_es', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_ca', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_de', models.TextField(null=True, verbose_name='description', blank=True)),
                ('designer', models.CharField(help_text='leave it blank if you are the designer', max_length=30, null=True, verbose_name='designer', blank=True)),
                ('start_year', models.PositiveIntegerField(verbose_name='start year')),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('published', models.DateField(null=True, verbose_name=b'publication date', blank=True)),
                ('countries', models.ManyToManyField(to='condottieri_scenarios.Country', through='condottieri_scenarios.Contender')),
                ('editor', models.ForeignKey(verbose_name='editor', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['setting', 'start_year'],
                'verbose_name': 'scenario',
                'verbose_name_plural': 'scenarios',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('title_en', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_es', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_ca', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('title_de', models.CharField(help_text='max. 128 characters', max_length=128, null=True, verbose_name='title', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_es', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_ca', models.TextField(null=True, verbose_name='description', blank=True)),
                ('description_de', models.TextField(null=True, verbose_name='description', blank=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('board', models.ImageField(upload_to=condottieri_scenarios.models.get_board_upload_path, verbose_name='board')),
                ('editor', models.ForeignKey(verbose_name='editor', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('permissions', models.ManyToManyField(related_name='allowed_users', verbose_name='permissions', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['slug'],
                'verbose_name': 'setting',
                'verbose_name_plural': 'settings',
            },
        ),
        migrations.CreateModel(
            name='Setup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unit_type', models.CharField(max_length=1, verbose_name='unit type', choices=[(b'A', 'Army'), (b'F', 'Fleet'), (b'G', 'Garrison')])),
                ('area', models.ForeignKey(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
                ('contender', models.ForeignKey(verbose_name='contender', to='condottieri_scenarios.Contender', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'initial setup',
                'verbose_name_plural': 'initial setups',
            },
        ),
        migrations.CreateModel(
            name='SpecialUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('static_title', models.CharField(max_length=50, verbose_name='static title')),
                ('title_en', models.CharField(max_length=50, null=True, verbose_name='title', blank=True)),
                ('title_es', models.CharField(max_length=50, null=True, verbose_name='title', blank=True)),
                ('title_ca', models.CharField(max_length=50, null=True, verbose_name='title', blank=True)),
                ('title_de', models.CharField(max_length=50, null=True, verbose_name='title', blank=True)),
                ('cost', models.PositiveIntegerField(verbose_name='cost')),
                ('power', models.PositiveIntegerField(verbose_name='power')),
                ('loyalty', models.PositiveIntegerField(verbose_name='loyalty')),
            ],
            options={
                'verbose_name': 'special unit',
                'verbose_name_plural': 'special units',
            },
        ),
        migrations.CreateModel(
            name='StormCell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row', models.PositiveIntegerField(verbose_name='row')),
                ('column', models.PositiveIntegerField(verbose_name='column')),
                ('area', models.OneToOneField(verbose_name='area', to='condottieri_scenarios.Area', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'storm cell',
                'verbose_name_plural': 'storm cells',
            },
        ),
        migrations.CreateModel(
            name='TradeRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'trade route',
                'verbose_name_plural': 'trade routes',
            },
        ),
        migrations.CreateModel(
            name='Treasury',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ducats', models.PositiveIntegerField(default=0, verbose_name='ducats')),
                ('double', models.BooleanField(default=False, verbose_name='double income')),
                ('contender', models.OneToOneField(verbose_name='contender', to='condottieri_scenarios.Contender', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'treasury',
                'verbose_name_plural': 'treasuries',
            },
        ),
        migrations.AddField(
            model_name='scenario',
            name='setting',
            field=models.ForeignKey(verbose_name='setting', to='condottieri_scenarios.Setting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='routestep',
            name='route',
            field=models.ForeignKey(to='condottieri_scenarios.TradeRoute', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='disabledarea',
            name='scenario',
            field=models.ForeignKey(verbose_name='scenario', to='condottieri_scenarios.Scenario', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='countryrandomincome',
            name='setting',
            field=models.ForeignKey(verbose_name='setting', to='condottieri_scenarios.Setting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='country',
            name='religion',
            field=models.ForeignKey(verbose_name='religion', blank=True, to='condottieri_scenarios.Religion', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='country',
            name='special_units',
            field=models.ManyToManyField(to='condottieri_scenarios.SpecialUnit', verbose_name='special units'),
        ),
        migrations.AddField(
            model_name='contender',
            name='country',
            field=models.ForeignKey(verbose_name='country', blank=True, to='condottieri_scenarios.Country', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='contender',
            name='scenario',
            field=models.ForeignKey(verbose_name='scenario', to='condottieri_scenarios.Scenario', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='configuration',
            name='setting',
            field=models.OneToOneField(editable=False, to='condottieri_scenarios.Setting', verbose_name='setting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='cityincome',
            name='scenario',
            field=models.ForeignKey(verbose_name='scenario', to='condottieri_scenarios.Scenario', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='area',
            name='borders',
            field=models.ManyToManyField(to='condottieri_scenarios.Area', verbose_name='borders', through='condottieri_scenarios.Border'),
        ),
        migrations.AddField(
            model_name='area',
            name='religion',
            field=models.ForeignKey(blank=True, to='condottieri_scenarios.Religion', help_text='used only in settings with the rule of religious wars', null=True, verbose_name='religion', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='area',
            name='setting',
            field=models.ForeignKey(verbose_name='setting', to='condottieri_scenarios.Setting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='aftoken',
            name='area',
            field=models.OneToOneField(to='condottieri_scenarios.Area', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='routestep',
            unique_together=set([('route', 'area')]),
        ),
        migrations.AlterUniqueTogether(
            name='home',
            unique_together=set([('contender', 'area')]),
        ),
        migrations.AlterUniqueTogether(
            name='disabledarea',
            unique_together=set([('scenario', 'area')]),
        ),
        migrations.AlterUniqueTogether(
            name='contender',
            unique_together=set([('country', 'scenario')]),
        ),
        migrations.AlterUniqueTogether(
            name='cityincome',
            unique_together=set([('city', 'scenario')]),
        ),
        migrations.AlterUniqueTogether(
            name='border',
            unique_together=set([('from_area', 'to_area')]),
        ),
        migrations.AlterUniqueTogether(
            name='area',
            unique_together=set([('setting', 'code')]),
        ),
    ]
