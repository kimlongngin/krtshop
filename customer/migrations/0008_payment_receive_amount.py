# Generated by Django 2.1.8 on 2019-09-08 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_auto_20190903_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='receive_amount',
            field=models.FloatField(default=0.0),
        ),
    ]
