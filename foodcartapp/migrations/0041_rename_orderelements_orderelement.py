# Generated by Django 3.2.4 on 2022-12-07 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20221203_2158'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrderElements',
            new_name='OrderElement',
        ),
    ]
