# Generated by Django 2.1.7 on 2019-02-21 10:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FlexForm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('disabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FlexFormData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timeOfCreate', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='FlexFormField',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('field_type', models.CharField(choices=[('text', 'text'), ('digit', 'digit')], max_length=10)),
                ('max_len', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2000)])),
                ('disabled', models.BooleanField(default=False)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FlexForm.FlexForm')),
            ],
        ),
        migrations.AddField(
            model_name='flexformdata',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FlexForm.FlexFormField'),
        ),
        migrations.AddField(
            model_name='flexformdata',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
