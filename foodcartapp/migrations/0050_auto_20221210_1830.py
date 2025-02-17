# Generated by Django 3.2.4 on 2022-12-10 15:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_auto_20221210_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pay_form',
            field=models.CharField(choices=[('right_now_pay', 'Электронно'), ('delivery_pay_cash', 'Наличными после доставки'), ('delivery_pay_card', 'Картой после доставки')], db_index=True, default='Наличными после доставки', max_length=50, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='called',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Время звонка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Время доставки'),
        ),
        migrations.AlterField(
            model_name='orderelement',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена товара'),
        ),
    ]
