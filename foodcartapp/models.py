from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from django.utils import timezone


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

class OrderQuerySet(models.QuerySet):

    def orders_price(self):
        orders = self.annotate(order_price=Sum(F('elements__price') * F('elements__quantity')))
        return orders

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

    address = models.CharField(
        verbose_name='Адрес',
        max_length=200,
    )

    NEW = 'New'
    DONE = 'Done'
    PROGRESS = 'Progress'
    GO = 'Go'

    STATUSES = (
        (NEW, 'Необработанный'),
        (DONE, 'Обработанный'),
        (PROGRESS, 'На сборке'),
        (GO, 'Доставляется'),
    )

    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=20,
        choices=STATUSES,
        default='Необработанный',
        db_index=True
    )


    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        blank=True,
    )

    registered_at = models.DateTimeField(
        verbose_name='Время создания заказа',
        default=timezone.now
    )

    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        db_index=True,
        blank=True,
        null=True
    )

    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        db_index=True,
        blank=True,
        null=True
    )

    RIGHT_NOW = 'right_now_pay'
    DELIVERY_CASH = 'delivery_pay_cash'
    DELIVERY_CARD = 'delivery_pay_card'

    FORMS = (
        (RIGHT_NOW, 'Электронно'),
        (DELIVERY_CASH, 'Наличными после доставки'),
        (DELIVERY_CARD, 'Картой после доставки')
    )

    pay_form = models.CharField(
        verbose_name='Способ оплаты',
        max_length=20,
        choices=FORMS,
        default=DELIVERY_CASH,
        db_index=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()
    class Meta:
        verbose_name = 'заказы'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname}, {self.lastname}, {self.address}'




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
        related_name='elements',
        verbose_name='Товар',
    )
    quantity = models.IntegerField(
        verbose_name='Количество данного товара',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name} - {self.order.firstname} {self.order.lastname}'

