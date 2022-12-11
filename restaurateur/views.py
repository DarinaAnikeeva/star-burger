from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, RestaurantMenuItem, Order, OrderElement


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })

def restaurants_with_order_products(order, order_elements):
    restaurants_lists = []
    items = RestaurantMenuItem.objects.prefetch_related('restaurant')
    for element in order_elements:
        menu_items = items.filter(product__id=element.product.id)
        restaurateurs_with_product = [item.restaurant.name for item in menu_items]
        restaurants_lists.append(restaurateurs_with_product)

    restaurants_for_order = restaurants_lists[0]
    for restaurant in restaurants_lists:
        restaurants_join = list(set(restaurants_for_order) & set(restaurant))
        restaurants_for_order = restaurants_join

    order_items = {
            'id': order.id,
            'status': order.get_status_display(),
            'pay_form': order.get_pay_form_display(),
            'price': order_elements.order_price(),
            'client': order.firstname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
            'restaurants': restaurants_for_order
        }

    return order_items


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.all()
    order_items = []
    for order in orders:
        if order.status != 'Done':
            order_elements = OrderElement.objects.filter(order=order).prefetch_related('product')
            if order.restaurant:
                order.status = 'Progress'
                order.save()

                order_items.append(
                    {
                        'id': order.id,
                        'status': order.get_status_display(),
                        'pay_form': order.get_pay_form_display(),
                        'price': order_elements.order_price(),
                        'client': order.firstname,
                        'phonenumber': order.phonenumber,
                        'address': order.address,
                        'comment': order.comment,
                        'restaurant': order.restaurant
                    }
                )
            else:
                order_item = restaurants_with_order_products(order, order_elements)
                order_items.append(order_item)

    return render(request, template_name='order_items.html', context={
        'order_items': order_items
    })
