# Generated by Django 3.2.4 on 2023-01-10 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_coordinates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinates',
            name='lat',
            field=models.FloatField(blank=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='lon',
            field=models.FloatField(blank=True, verbose_name='Долгота'),
        ),
    ]
