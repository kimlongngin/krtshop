# Generated by Django 2.1.8 on 2019-08-27 05:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_auto_20190814_0727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='province_location', to='location.Location'),
        ),
    ]
