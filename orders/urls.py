from django.urls import path
from . import views


urlpatterns = [

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

    path(
        'shop-orders/',
        views.shop_orders,
        name='shop_orders'
    ),

    path(
        'update-status/<int:order_id>/',
        views.update_order_status,
        name='update_order_status'
    ),

    path(
        '<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        'payment/<int:order_id>/',
        views.payment_page,
        name='payment_page'
    ),

    path(
        'payment/verify/',
        views.verify_payment,
        name='verify_payment'
    ),

    path(
        'payment/result/<int:order_id>/',
        views.payment_result,
        name='payment_result'
    ),

    path(
        'cancel/<int:order_id>/',
        views.cancel_order,
        name='cancel_order'
    ),

    path('notifications/',
         views.notifications,
         name='notifications'),

    path(
        'notifications/read/<int:notification_id>/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

]