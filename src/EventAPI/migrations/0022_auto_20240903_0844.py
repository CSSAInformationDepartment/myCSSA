# Generated by Django 3.1.12 on 2024-09-03 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EventAPI', '0021_auto_20211220_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='eventName',
            field=models.CharField(max_length=40, unique=True, verbose_name='活动名称'),
        ),
    ]
