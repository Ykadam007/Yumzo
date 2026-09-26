from django.urls import path
from . import views

urlpatterns = [



    path(
        'create/',
        views.create_shop,
        name='create_shop'
    ),

    path(
        'profile/',
        views.shop_profile,
        name='shop_profile'
    ),

    path(
        'list/',
        views.shop_list,
        name='shop_list'
    ),
]