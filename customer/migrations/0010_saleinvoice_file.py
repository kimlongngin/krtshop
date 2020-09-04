# Generated by Django 2.1.8 on 2019-09-19 15:34

import customer.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0009_auto_20190908_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleinvoice',
            name='file',
            field=models.FileField(blank=True, upload_to=customer.models.content_file_name, validators=[customer.models.validate_file_pdf]),
        ),
    ]
