from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Order
from .models import OrderElement
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem

class OrderElementInline(admin.TabularInline):
    model = OrderElement
    extra = 0
    readonly_fields = [
        'product_sum',
        'catalog_price'
    ]

    def product_sum(self, obj):
        if obj.quantity and obj.price:
            sum = obj.price * obj.quantity
            return sum

    def catalog_price(self, obj):
        return obj.product.price


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = [
        'price'
    ]

    inlines = [
        OrderElementInline
    ]


    def price(self, obj):
        price = 0
        for element in obj.elements.all():
            if element.quantity and element.price:
                price += element.quantity * element.price
        return price

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            if url_has_allowed_host_and_scheme(request.GET['next'], None):
                return redirect(request.GET['next'])
            else:
                return res


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
