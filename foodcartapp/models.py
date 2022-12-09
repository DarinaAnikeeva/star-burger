from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Count, F


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name




class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    firstname = models.CharField(
        verbose_name='Имя',
        max_length=20,
    )
    lastname = models.CharField(
        verbose_name='Фамилия',
        max_length=20,
    )
    phonenumber = PhoneNumberField(
        'Номер телефона',
        region='RU',
        max_length=20,
        db_index=True)

    address = models.TextField(
        verbose_name='Адрес',
    )

    STATUSES = (
        ('New', 'Необработанный'),
        ('Done', 'Обработанный'),
        ('Progress', 'На сборке'),
        ('Go', 'Доставляется'),
    )

    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=20,
        choices=STATUSES,
        default='Необработанный',
        db_index=True
    )

    class Meta:
        verbose_name = 'заказы'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname}, {self.lastname}, {self.address}'


class OrderElementQuerySet(models.QuerySet):

    def order_price(self):
        order_elements = self.annotate(element_price=F('price') * F('quantity'))
        price = 0
        for element in order_elements:
            price += element.element_price
        return price


class OrderElement(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='elements',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='Товар',
    )
    quantity = models.IntegerField(
        verbose_name='Количество',
    )

    objects = OrderElementQuerySet.as_manager()

    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name} - {self.order.firstname} {self.order.lastname}'
