# Generated by Django 3.1.12 on 2023-08-24 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myCSSAhub', '0021_auto_20210814_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountmerchant',
            name='merchant_Category',
            field=models.CharField(blank=True, choices=[('无', '无'), ('餐饮美食', '餐饮美食'), ('便捷生活', '便捷生活'), ('休闲娱乐', '休闲娱乐'), ('生活服务', '生活服务'), ('消费购物', '消费购物'), ('美丽Buff', '美丽Buff')], max_length=10, null=True, verbose_name='折扣商家种类'),
        ),
        migrations.AlterField(
            model_name='discountmerchant',
            name='merchant_level',
            field=models.CharField(blank=True, choices=[('无', '无'), ('钻石商家', '钻石商家'), ('金牌商家', '金牌商家'), ('银牌商家', '银牌商家')], max_length=10, null=True, verbose_name='赞助商等级'),
        ),
    ]
