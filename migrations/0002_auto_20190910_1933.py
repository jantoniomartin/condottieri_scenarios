# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-10 19:33
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('condottieri_scenarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='name_en',
            field=models.CharField(default='', max_length=25, verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cityrandomincome',
            name='income_list',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='List must have 6 comma separated numbers', regex='^([0-9]+,\\s*){5}[0-9]+$')], verbose_name='income list'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name_en',
            field=models.CharField(default='', max_length=50, verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='countryrandomincome',
            name='income_list',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='List must have 6 comma separated numbers', regex='^([0-9]+,\\s*){5}[0-9]+$')], verbose_name='income list'),
        ),
        migrations.AlterField(
            model_name='religion',
            name='name_en',
            field=models.CharField(default='', max_length=50, verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scenario',
            name='description_en',
            field=models.TextField(default='', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scenario',
            name='published',
            field=models.DateField(blank=True, null=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='title_en',
            field=models.CharField(default='', help_text='max. 128 characters', max_length=128, verbose_name='title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setting',
            name='description_en',
            field=models.TextField(default='', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setting',
            name='title_en',
            field=models.CharField(default='', help_text='max. 128 characters', max_length=128, verbose_name='title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setup',
            name='unit_type',
            field=models.CharField(choices=[('A', 'Army'), ('F', 'Fleet'), ('G', 'Garrison')], max_length=1, verbose_name='unit type'),
        ),
        migrations.AlterField(
            model_name='specialunit',
            name='title_en',
            field=models.CharField(default='', max_length=50, verbose_name='title'),
            preserve_default=False,
        ),
    ]
