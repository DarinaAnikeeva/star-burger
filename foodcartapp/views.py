import phonenumbers

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.test import APITestCase
from rest_framework import status

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


def check_order_json(order_info):
    try:
        order_info['products']
        order_info['firstname']
        order_info['lastname']
        order_info['address']
        order_info['phonenumber']
    except:
        return Response({'products, firstname, lastname, phonenumber, address': 'Обязательное поле.'})

    if order_info['products'] == []:
        return Response({"products": "Этот список не может быть пустым."})

    elif isinstance(order_info['products'], str):
        return Response({'products': 'Ожидался list, но был получени str'})

    elif order_info['products'] == None:
        return Response({"products": "Это поле не может быть пустым."})

    if (order_info['firstname'] and
        order_info['lastname'] and
        order_info['address'] and
        order_info['phonenumber']) == 'null':
        return Response({'firstname, lastname, phonenumber, address': 'Это поле не может быть пустым'})

    if order_info['phonenumber'] == "":
        return Response({'phonenumber': 'Это поле не может быть пустым'})

    if isinstance(order_info['firstname'], list):
        return  Response({'firstname': 'Not a valid string.'})


@api_view(['POST'])
def register_order(request):
    order_info = request.data
    check_order_json(order_info)
    try:
        order_info['products']
        order_info['firstname']
        order_info['lastname']
        order_info['address']
        order_info['phonenumber']
    except:
        return Response({'products, firstname, lastname, phonenumber, address': 'Обязательное поле.'})

    if order_info['products'] == []:
        return Response({"products": "Этот список не может быть пустым."})

    elif isinstance(order_info['products'], str):
        return Response({'products': 'Ожидался list, но был получени str'})

    elif order_info['products'] == None:
        return Response({"products": "Это поле не может быть пустым."})

    if (order_info['firstname'] and
        order_info['lastname'] and
        order_info['address'] and
        order_info['phonenumber']) == None:
        return Response({'firstname, lastname, phonenumber, address': 'Это поле не может быть пустым'})

    if isinstance(order_info['firstname'], list):
        return Response({'firstname': 'Not a valid string.'})
    if order_info['firstname'] == None:
        return Response({"firstname": "Это поле не может быть пустым."})

    try:
        client_phone = phonenumbers.parse(order_info['phonenumber'], 'RU')
        if phonenumbers.is_valid_number(client_phone):
            phonenumber = order_info['phonenumber']
        else:
            return Response({'phonenumber': 'Введен некорректный номер телефона'})
    except:
        return Response({'phonenumber': 'Введен некорректный номер телефона'})

    order = Order.objects.create(
        name=order_info['firstname'],
        surname=order_info['lastname'],
        phonenumber=phonenumber,
        address=order_info['address'],
    )

    for product in order_info['products']:
        max_product_id = Product.objects.count()
        product_id = int(product.get('product'))
        if product_id > max_product_id:
            return Response({'products': f'Недопустимый первичный ключ "{product_id}"'})
        get_product = Product.objects.get(id=product.get('product'))
        order_elements = OrderElements.objects.create(
            order=order,
            name=get_product.name,
            quantity=product['quantity']
        )

    return Response()
