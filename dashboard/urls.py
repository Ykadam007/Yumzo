from django.urls import path
from . import views

urlpatterns = [
    path(
        'customer/',
        views.customer_dashboard,
        name='customer_dashboard'
    ),

    path(
        'shop/',
        views.shop_dashboard,
        name='shop_dashboard'
    ),

    path(
        'admin/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'manage-shops/',
        views.manage_shops,
        name='manage_shops'
    ),

    path(
        'manage-shops/<int:shop_id>/approve/',
        views.approve_shop,
        name='approve_shop'
    ),

    path(
        'manage-shops/<int:shop_id>/reject/',
        views.reject_shop,
        name='reject_shop'
    ),

    path(
        'manage-users/',
        views.manage_users,
        name='manage_users'
    ),

    path(
        'manage-products/',
        views.manage_products,
        name='manage_products'
    ),

    path(
        'manage-orders/',
        views.manage_orders,
        name='manage_orders'
    ),

    path(
        'manage-orders/<int:order_id>/',
        views.admin_order_detail,
        name='admin_order_detail'
    ),

    path('reviews/',
         views.manage_reviews,
         name='manage_reviews'),

    path(
        'reviews/delete/<int:review_id>/',
        views.delete_review,
        name='delete_review'
    ),

    path(
        'categories/',
        views.manage_categories,
        name='manage_categories'
    ),

    path(
        'categories/add/',
        views.add_category,
        name='add_category'
    ),

    path(
        'categories/edit/<int:category_id>/',
        views.edit_category,
        name='edit_category'
    ),

    path(
        'categories/toggle/<int:category_id>/',
        views.toggle_category,
        name='toggle_category'
    ),

    path(
        'products/toggle/<int:product_id>/',
        views.toggle_product,
        name='toggle_product'
    ),

    path(
        'products/delete/<int:product_id>/',
        views.delete_product_admin,
        name='delete_product_admin'
    ),

    path(
        'products/edit/<int:product_id>/',
        views.edit_product_admin,
        name='edit_product_admin'
    ),

    path(
        'users/toggle/<int:user_id>/',
        views.toggle_user_status,
        name='toggle_user_status'
    ),
]