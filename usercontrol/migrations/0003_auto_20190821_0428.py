# Generated by Django 2.1.8 on 2019-08-21 04:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usercontrol', '0002_auto_20190821_0424'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercontrol',
            old_name='user',
            new_name='name',
        ),
    ]