# Generated by Django 4.2.5 on 2023-12-14 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0002_alter_group_created_at_alter_group_modified_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='students',
            field=models.JSONField(default=None, verbose_name='Students'),
        ),
    ]
