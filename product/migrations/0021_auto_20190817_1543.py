# Generated by Django 2.1.8 on 2019-08-17 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_producttype_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productinstock',
            old_name='amount_per_unit',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='productinstockhistory',
            old_name='amount_per_unit',
            new_name='amount',
        ),
    ]
