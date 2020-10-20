# Generated by Django 2.1.3 on 2018-12-28 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyUsers',
            fields=[
                ('recordId', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('identiyConfirmed', models.BooleanField(default=False, verbose_name='会员身份状态')),
                ('isValid', models.BooleanField(default=False, verbose_name='账号有效性')),
                ('isAdult', models.BooleanField(default=False, verbose_name='是否成年')),
                ('firstNameEN', models.CharField(max_length=50, verbose_name='英文名')),
                ('lastNameEN', models.CharField(max_length=50, verbose_name='英文姓')),
                ('firstNameCN', models.CharField(max_length=50, null=True, verbose_name='中文名')),
                ('lastNameCN', models.CharField(max_length=50, null=True, verbose_name='中文姓')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O', max_length=5, verbose_name='性别')),
                ('dateOfBirth', models.DateTimeField(null=True, verbose_name='生日')),
                ('joinDate', models.DateTimeField(verbose_name='入会日期')),
                ('studentId', models.CharField(max_length=10, verbose_name='学生证号')),
                ('membershipId', models.CharField(max_length=10, null=True, verbose_name='会员卡号')),
                ('telNumber', models.CharField(max_length=12, null=True, verbose_name='联系电话')),
                ('email', models.CharField(max_length=30, null=True, verbose_name='电子邮箱')),
                ('address', models.CharField(max_length=100, null=True, verbose_name='地址')),
                ('postcode', models.CharField(max_length=4, null=True, verbose_name='邮编')),
                ('originate', models.CharField(max_length=20, null=True, verbose_name='籍贯')),
                ('majorName', models.CharField(max_length=100, null=True, verbose_name='专业')),
            ],
        ),
    ]