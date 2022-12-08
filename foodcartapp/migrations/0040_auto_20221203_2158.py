# Generated by Django 3.2.4 on 2022-12-03 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20221203_1759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderelements',
            name='name',
        ),
        migrations.AddField(
            model_name='orderelements',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.product', verbose_name='продукт'),
            preserve_default=False,
        ),
    ]
