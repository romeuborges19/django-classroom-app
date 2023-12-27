# Generated by Django 4.2.5 on 2023-12-26 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0005_approvedlist_missing_list_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approvedlist',
            name='missing_list',
        ),
        migrations.AddField(
            model_name='approvedlist',
            name='not_missing_list',
            field=models.JSONField(default=None, verbose_name='Not missing students list'),
        ),
    ]