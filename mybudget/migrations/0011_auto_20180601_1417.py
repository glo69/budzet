# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-01 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybudget', '0010_auto_20180601_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podtyp_wydatku',
            name='podtyp_wydatku',
            field=models.CharField(max_length=45, unique=True),
        ),
        migrations.AlterField(
            model_name='typ_wydatku',
            name='nazwa_wydatku',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]