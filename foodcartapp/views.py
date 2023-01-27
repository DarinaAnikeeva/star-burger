import logging
import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.serializers import ModelSerializer
from django.db import transaction
from star_burger.settings import YANDEX_API_KEY

from .models import Order
from .models import OrderElement
from .models import Product
from restaurateur.models import Coordinates


class MyError(TypeError):
    def __init__(self, text):
        self.txt = text

@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return Response([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


class OrderElementsSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderElementsSerializer(many=True,
                                       allow_empty=False,
                                       write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'address', 'phonenumber', 'products']


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return MyError('Введён некоректный адрес')

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_info = serializer.validated_data
    address = order_info['address']

    order = Order.objects.create(
        firstname=order_info['firstname'],
        lastname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=address,
    )
    try:
        coordinates = Coordinates.objects.get_or_create(
            address=address,
        )
    except Coordinates.DoesNotExist:
        try:
            lon, lat = fetch_coordinates(YANDEX_API_KEY, address)
            coordinates = Coordinates.objects.create(
                address=address,
                lon=lon,
                lat=lat,
            )
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            pass1
        except MyError as err:
            logging.error(err)
            pass

    objs = [
        OrderElement(
            order=order,
            product=product_param.get('product'),
            quantity=product_param.get('quantity'),
            price=product_param.get('product').price
        )
        for product_param in order_info['products']
    ]
    OrderElement.objects.bulk_create(objs)

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=200)


