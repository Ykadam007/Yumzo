from django.urls import path
from . import views


urlpatterns = [

    path(
        'add/',
        views.add_product,
        name='add_product'
    ),

    path(
        '',
        views.product_list,
        name='product_list'
    ),

    path(
        'edit/<int:product_id>/',
        views.edit_product,
        name='edit_product'
    ),

    path(
        'delete/<int:product_id>/',
        views.delete_product,
        name='delete_product'
    ),

    path(
        'marketplace/',
        views.marketplace,
        name='marketplace'
    ),

    path(
        'detail/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

path(
    'shop/<int:shop_id>/',
    views.shop_products,
    name='shop_products'
),
]