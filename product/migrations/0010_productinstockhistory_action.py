# Generated by Django 2.1.8 on 2019-08-11 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_auto_20190811_0753'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinstockhistory',
            name='action',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]