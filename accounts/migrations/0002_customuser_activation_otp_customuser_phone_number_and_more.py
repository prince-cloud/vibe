# Generated by Django 4.2 on 2023-08-19 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='activation_otp',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(db_index=True, default=1, max_length=14, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='token',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='customuser',
            name='token_reason',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
