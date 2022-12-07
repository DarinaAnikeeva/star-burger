from rest_framework.renderers import JSONRenderer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.serializers import ModelSerializer


from .models import Order
from .models import OrderElement
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
        model = OrderElement
        fields = ['product', 'quantity']

class OrderSerializer(ModelSerializer):
    products = OrderElementsSerializer(many=True,
                                       allow_empty=False,
                                       write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'address', 'phonenumber', 'products']


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_info = serializer.validated_data

    order = Order.objects.create(
        firstname=order_info['firstname'],
        lastname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=order_info['address'],
    )

    for product_param in order_info['products']:
        quantity = product_param.get('quantity')
        product = product_param.get('product')
        order_elements = OrderElement.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=200)
