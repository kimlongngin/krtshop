# Generated by Django 2.1.8 on 2019-08-09 03:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20190809_0314'),
    ]

    operations = [
        migrations.AddField(
            model_name='subproductimage',
            name='description',
            field=models.TextField(default=datetime.datetime(2019, 8, 9, 3, 46, 49, 807788, tzinfo=utc)),
            preserve_default=False,
        ),
    ]