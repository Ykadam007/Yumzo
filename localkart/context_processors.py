from cart.models import Cart
from orders.models import Notification


def cart_count(request):
    count = 0

    if request.user.is_authenticated and request.user.role == 'customer':
        cart = Cart.objects.filter(
            customer=request.user
        ).first()

        if cart:
            count = sum(
                item.quantity
                for item in cart.items.all()
            )

    unread_notifications = 0

    if request.user.is_authenticated and request.user.role == 'customer':
        unread_notifications = Notification.objects.filter(
            customer=request.user,
            is_read=False
        ).count()

    return {
        'cart_count': count,
        'unread_notifications': unread_notifications,
    }