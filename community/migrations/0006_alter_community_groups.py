# Generated by Django 4.2 on 2023-08-28 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0005_rename_coummunity_announcement_community'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='groups',
            field=models.ManyToManyField(related_name='community', to='community.group'),
        ),
    ]
