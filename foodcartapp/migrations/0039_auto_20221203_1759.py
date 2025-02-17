# Generated by Django 3.2.4 on 2022-12-03 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderelements'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='surname',
            new_name='lastname',
        ),
        migrations.AlterField(
            model_name='orderelements',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='orderelements',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='foodcartapp.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='orderelements',
            name='quantity',
            field=models.IntegerField(verbose_name='Количество'),
        ),
    ]
