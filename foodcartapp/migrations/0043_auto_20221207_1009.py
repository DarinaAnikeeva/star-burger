# Generated by Django 3.2.4 on 2022-12-07 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20221207_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderelement',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Цена товара'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderelement',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.product', verbose_name='Товар'),
        ),
    ]
