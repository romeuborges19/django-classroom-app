# Generated by Django 4.2.5 on 2023-12-28 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0011_alter_approvedlist_approved_list_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvedlist',
            name='unknown_list',
            field=models.JSONField(default=None, null=True, verbose_name='List of unknown students'),
        ),
    ]
