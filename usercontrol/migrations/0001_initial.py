# Generated by Django 2.1.8 on 2019-08-21 04:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import usercontrol.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=250)),
                ('avatar', models.FileField(blank=True, upload_to=usercontrol.models.user_directory_path, validators=[usercontrol.models.validate_file_extension])),
                ('age', models.IntegerField(default=0)),
                ('present_address', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('is_status', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
