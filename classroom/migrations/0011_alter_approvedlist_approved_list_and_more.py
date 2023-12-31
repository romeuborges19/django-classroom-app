# Generated by Django 4.2.5 on 2023-12-27 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0010_remove_approvedlist_not_missing_list_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvedlist',
            name='approved_list',
            field=models.JSONField(default=None, null=True, verbose_name='List of approved students'),
        ),
        migrations.AlterField(
            model_name='approvedlist',
            name='enrolled_list',
            field=models.JSONField(default=None, null=True, verbose_name='List of enrolled students'),
        ),
        migrations.AlterField(
            model_name='approvedlist',
            name='missing_list',
            field=models.JSONField(default=None, null=True, verbose_name='List of missing students'),
        ),
    ]
