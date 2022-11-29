from pprint import pprint

from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static

from .models import Order
from .models import OrderElements
from .models import Product

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


def product_name(product_id):
    product = Product.objects.get(id=product_id)
    return product.name

@api_view(['POST'])
def register_order(request):
    order_info = request.data
    pprint(order_info)
    order = Order.objects.create(
        name=order_info['firstname'],
        surname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=order_info['address'],
    )

    for product in order_info['products']:
        order_elements = OrderElements.objects.create(
            order=order,
            name=product_name(product['product']),
            quantity=product['quantity']
        )

    order_dict = {
        'products': [product for product in order_info['products']],
        'firstname': order_info['firstname'],
        'lastname': order_info['lastname'],
        'phonenumber': order_info['phonenumber'],
        'address': order_info['address']
    }
    return Response(order_dict)
