from django.db import models

class Coordinates(models.Model):
    address = models.CharField(
        verbose_name='адрес',
        max_length=200,
    )
    lon = models.FloatField(
        verbose_name='Долгота',
        blank=True,
    )
    lat = models.FloatField(
        verbose_name='Широта',
        blank=True,
    )
    class Meta:
        verbose_name = 'координаты заказа'
        verbose_name_plural = 'координаты заказа'

    def __str__(self):
        return self.address
