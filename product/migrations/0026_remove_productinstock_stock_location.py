# Generated by Django 2.1.8 on 2019-09-09 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_remove_productinstock_controller'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinstock',
            name='stock_location',
        ),
    ]
