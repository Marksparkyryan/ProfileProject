# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2019-10-09 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20191008_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='owls/pinkowl.png', upload_to='avatars'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cats_or_dogs',
            field=models.CharField(choices=[('Cats', 'Cats'), ('Dogs', 'Dogs')], default='Dogs', max_length=3),
        ),
        migrations.AlterField(
            model_name='profile',
            name='favourite_colour',
            field=models.CharField(blank=True, default="I'm boring, I don't like colours.", max_length=32, null=True),
        ),
    ]
