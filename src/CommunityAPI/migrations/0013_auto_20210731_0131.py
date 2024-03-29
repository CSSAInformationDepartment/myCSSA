# Generated by Django 3.1.12 on 2021-07-30 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CommunityAPI', '0012_userinformation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'permissions': (('can_handle_report', 'Can handle report'),)},
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('REPLY', '回复'), ('CENSOR', '屏蔽'), ('DECENSOR', '解除屏蔽')], max_length=100, verbose_name='通知类型'),
        ),
    ]
