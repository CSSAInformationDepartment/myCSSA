# Generated by Django 2.1.7 on 2019-03-06 03:58

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('myCSSAhub', '0011_auto_20190302_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountmerchant',
            name='merchant_add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 6, 3, 58, 5, 884255, tzinfo=utc), verbose_name='商户加入时间'),
        ),
    ]