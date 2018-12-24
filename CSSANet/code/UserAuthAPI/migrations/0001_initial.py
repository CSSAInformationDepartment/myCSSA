# Generated by Django 2.1.3 on 2018-12-02 04:47

import UserAuthAPI.models
from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSSACommitteProfile',
            fields=[
                ('tableId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=False)),
                ('CommenceDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CSSADept',
            fields=[
                ('deptId', models.AutoField(primary_key=True, serialize=False)),
                ('deptName', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CSSARole',
            fields=[
                ('roleId', models.AutoField(primary_key=True, serialize=False)),
                ('roleFlag', models.CharField(max_length=3)),
                ('roleName', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UniMajor',
            fields=[
                ('uniMajorId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('majorName', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserAcademic',
            fields=[
                ('academicRecId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timeOfCreate', models.DateTimeField(auto_now_add=True)),
                ('degree', models.CharField(choices=[('CR', 'Certificate'), ('DP', 'Diploma'), ('FN', 'Foundation'), ('BA', 'Bachelor'), ('MA', 'Master'), ('JD', 'Jurum Doctor'), ('MD', 'Medical Doctor'), ('PhD', 'Doctor of Philosophy')], default='BA', max_length=32, verbose_name='学位')),
                ('uniMajor', models.ForeignKey(on_delete=None, to='UserAuthAPI.UniMajor', verbose_name='专业')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=UserAuthAPI.models._GetUserDir, verbose_name='头像')),
                ('infocardBg', models.ImageField(blank=True, null=True, upload_to=UserAuthAPI.models._GetUserDir, verbose_name='名片背景')),
                ('identiyConfirmed', models.BooleanField(default=False, verbose_name='会员身份状态')),
                ('isValid', models.BooleanField(default=False, verbose_name='账号有效性')),
                ('firstNameEN', models.CharField(max_length=50, verbose_name='英文名')),
                ('lastNameEN', models.CharField(max_length=50, verbose_name='英文姓')),
                ('firstNameCN', models.CharField(blank=True, max_length=50, null=True, verbose_name='中文名')),
                ('lastNameCN', models.CharField(blank=True, max_length=50, null=True, verbose_name='中文姓')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O', max_length=50)),
                ('dateOfBirth', models.DateField(null=True, verbose_name='生日')),
                ('joinDate', models.DateTimeField(auto_now_add=True)),
                ('studentId', models.CharField(max_length=10, verbose_name='学生证号')),
                ('membershipId', models.CharField(blank=True, max_length=10, null=True, verbose_name='会员卡号')),
                ('address', models.CharField(max_length=150, null=True, verbose_name='地址')),
                ('postcode', models.CharField(max_length=4, null=True, verbose_name='邮编')),
                ('originate', models.CharField(max_length=20, null=True, verbose_name='籍贯')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100, unique=True, verbose_name='电子邮箱')),
                ('telNumber', models.CharField(max_length=16, null=True, verbose_name='联系电话')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', UserAuthAPI.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useracademic',
            name='userProfile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cssacommitteprofile',
            name='Department',
            field=models.ForeignKey(on_delete=None, to='UserAuthAPI.CSSADept'),
        ),
        migrations.AddField(
            model_name='cssacommitteprofile',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]