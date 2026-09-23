from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
        'shop',
        'total_amount',
        'payment_method',
        'payment_status',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'payment_status',
        'created_at',
    )

    search_fields = (
        'customer__username',
        'shop__name',
        'phone',
    )

    inlines = [
        OrderItemInline
    ]



@admin.register(Payment)

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'razorpay_order_id',
        'razorpay_payment_id',
        'amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'razorpay_order_id',
        'razorpay_payment_id',
        'order__customer__username',
    )