import logging

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance
from foodcartapp.views import fetch_coordinates
from star_burger.settings import YANDEX_API_KEY
from foodcartapp.views import MyError

from foodcartapp.models import Product, Restaurant, RestaurantMenuItem, Order, OrderElement
from restaurateur.models import Coordinates


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

def get_restaurant_distance(restaurant):
    return restaurant['distance']


def find_distances(client_address, restautants):
    coordinates = Coordinates.objects.all()
    for coords in coordinates:
        if coords.address == client_address:
            client_coordinates = (
                coords.lat,
                coords.lon
            )

    restaurants_for_order_distance = []
    for restautant in restautants:
        try:
            for coords in coordinates:
                if coords.address == restautant.address:
                    restautant_coordinates = (
                        coords.lat,
                        coords.lon
                    )
        except Coordinates.DoesNotExist:
            try:
                lon, lat = fetch_coordinates(YANDEX_API_KEY, restautant.address)
                restautant_coords = Coordinates.objects.create(
                    address=restautant.address,
                    lon=lon,
                    lat=lat
                )[0]
            except MyError as err:
                logging.error(err)
                pass

        distance_from_restaurant_to_client = round(distance.distance(
            client_coordinates,
            restautant_coordinates
        ).km, 1)
        restaurants_for_order_distance.append(
            {
                'name': restautant.name,
                'distance': distance_from_restaurant_to_client
            }
        )
    return sorted(restaurants_for_order_distance,
                  key=get_restaurant_distance)

def restaurants_with_order_products(order_elements):
    restaurants_lists = []
    items = RestaurantMenuItem.objects.prefetch_related('restaurant')
    for element in order_elements:
        for item in items:
            if item.product == element.product:
                restaurants_lists.append(item.restaurant)

    return list(set(restaurants_lists))


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.prefetch_related('restaurant')\
                          .prefetch_related('elements__product')\
                          .orders_price()
    order_items = []
    for order in orders:
        if order.status != 'Done':
            order_elements = OrderElement.objects.filter(order=order).prefetch_related('product')\
                                                                     .prefetch_related('order')
            if order.restaurant:
                restaurant = order.restaurant
                restaurants = None
                PROCESS = 'Process'
                order.order_status = PROCESS
                order.save()

            else:
                restaurants_for_order = restaurants_with_order_products(order_elements)
                restaurants = find_distances(order.address, restaurants_for_order)
                restaurant = None
            order_items.append(
                {
                    'id': order.id,
                    'status': order.get_status_display(),
                    'pay_form': order.get_pay_form_display(),
                    'price': order.order_price,
                    'client': order.firstname,
                    'phonenumber': order.phonenumber,
                    'address': order.address,
                    'comment': order.comment,
                    'estaurant': restaurant,
                    'restaurants': restaurants,
                }
            )

    return render(request, template_name='order_items.html', context={
        'order_items': order_items
    })
