# Generated by Django 4.2 on 2023-08-20 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_alter_community_options_alter_group_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='announcement',
            old_name='coummunity',
            new_name='community',
        ),
    ]
