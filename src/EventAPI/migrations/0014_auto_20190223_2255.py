# Generated by Django 2.1.7 on 2019-02-23 22:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EventAPI', '0013_auto_20190223_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventattendentinfoform',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EventAPI.Event', verbose_name='绑定新活动'),
        ),
    ]