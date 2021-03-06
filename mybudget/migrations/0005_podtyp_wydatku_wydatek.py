# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 18:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('mybudget', '0004_baza_wydatkow_dochod'),
    ]

    operations = [
        migrations.CreateModel(
            name='Podtyp_wydatku',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('podtyp_wydatku', models.CharField(max_length=45)),
                ('nazwa_wydatku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mybudget.Typ_wydatku')),
            ],
        ),
        migrations.CreateModel(
            name='Wydatek',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazwa_wydatku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mybudget.Typ_wydatku')),
                ('podtyp_wydatku', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='nazwa_wydatku', chained_model_field='nazwa_wydatku', on_delete=django.db.models.deletion.CASCADE, to='mybudget.Podtyp_wydatku')),
            ],
        ),
    ]
