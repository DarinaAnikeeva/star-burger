import phonenumbers

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.serializers import ModelSerializer


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


class OrderElementsSerializer(ModelSerializer):
    class Meta:
        model = OrderElements
        fields = ['product', 'quantity']

class OrderSerializer(ModelSerializer):
    products = OrderElementsSerializer(many=True,
                                       allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'address', 'phonenumber', 'products']


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_info = serializer.validated_data
    # try:
    #     client_phone = phonenumbers.parse(order_info['phonenumber'], 'RU')
    #     if phonenumbers.is_valid_number(client_phone):
    #         phonenumber = order_info['phonenumber']
    #     else:
    #         return Response({'phonenumber': 'Введен некорректный номер телефона'})
    # except:
    #     return Response({'phonenumber': 'Введен некорректный номер телефона'})

    order = Order.objects.create(
        firstname=order_info['firstname'],
        lastname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=order_info['address'],
    )

    for product_param in order_info['products']:
        max_product_id = Product.objects.count()
        product_id = int(product_param.get('product'))
        if product_id > max_product_id:
            return Response({'products': f'Недопустимый первичный ключ "{product_id}"'})
        product = Product.objects.get(id=product_id)
        order_elements = OrderElements.objects.create(
            order=order,
            product=product,
            quantity=product_param['quantity']
        )

    return Response()
