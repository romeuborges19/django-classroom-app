# Generated by Django 4.2.5 on 2023-12-26 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0006_remove_approvedlist_missing_list_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approvedlist',
            name='not_missing_list',
        ),
    ]
