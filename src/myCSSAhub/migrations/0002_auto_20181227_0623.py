# Generated by Django 2.1.3 on 2018-12-27 06:23

from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myCSSAhub', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='NotificationText',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.CharField(max_length=200, null=True, verbose_name='站内信内容')),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='messageID',
            field=models.ForeignKey(on_delete=models.DO_NOTHING, to='myCSSAhub.NotificationText'),
        ),
        migrations.AddField(
            model_name='notification',
            name='recID',
            field=models.ForeignKey(on_delete=models.DO_NOTHING, related_name='接受者id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='sendID',
            field=models.ForeignKey(on_delete=models.DO_NOTHING, related_name='发送者id', to=settings.AUTH_USER_MODEL),
        ),
    ]
