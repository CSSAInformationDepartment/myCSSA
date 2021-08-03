# Generated by Django 3.1.12 on 2021-08-02 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuthAPI', '0019_auto_20210709_1833'),
        ('CommunityAPI', '0015_auto_20210802_0202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinformation',
            name='user_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='UserAuthAPI.userprofile', verbose_name='用户的id'),
        ),
        migrations.RenameField(
            model_name='userinformation',
            old_name='user_id',
            new_name='user',
        ),
    ]