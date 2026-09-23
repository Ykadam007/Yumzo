from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

import razorpay
from django.conf import settings
from cart.models import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem, Payment,Notification, OrderStatusHistory
from django.http import JsonResponse

@login_required
def checkout(request):

    if request.user.role != 'customer':
        return redirect('customer_dashboard')

    cart = get_object_or_404(
        Cart.objects.prefetch_related('items__product__shop'),
        customer=request.user
    )

    cart_items = cart.items.select_related(
        'product',
        'product__shop'
    )

    if not cart_items.exists():
        return redirect('cart_detail')

    # Check stock before creating orders
    for item in cart_items:

        product = item.product

        if (
            not product.is_available
            or product.stock < item.quantity
            or product.shop.approval_status != 'approved'
        ):
            return redirect('cart_detail')

    # Group cart items by shop
    shops_items = {}

    for item in cart_items:

        shop_id = item.product.shop.id

        if shop_id not in shops_items:
            shops_items[shop_id] = []

        shops_items[shop_id].append(item)


    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            delivery_fee = 40

            for shop_id, items in shops_items.items():

                shop = items[0].product.shop

                subtotal = sum(
                    item.subtotal for item in items
                )

                total_amount = subtotal + delivery_fee


                order = Order.objects.create(

                    customer=request.user,

                    shop=shop,

                    full_name=form.cleaned_data['full_name'],

                    phone=form.cleaned_data['phone'],

                    address=form.cleaned_data['address'],

                    city=form.cleaned_data['city'],

                    pincode=form.cleaned_data['pincode'],

                    landmark=form.cleaned_data['landmark'],

                    subtotal=subtotal,

                    delivery_fee=delivery_fee,

                    total_amount=total_amount,

                    payment_method=form.cleaned_data['payment_method'],

                    payment_status='pending',

                    status='placed',
                )

                OrderStatusHistory.objects.create(
                    order=order,
                    status='placed',
                    changed_by=request.user
                )

                if order.payment_method == 'online':
                    Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        status='pending',
                    )


                # Create order items
                for item in items:

                    product = item.product

                    OrderItem.objects.create(

                        order=order,

                        product=product,

                        product_name=product.name,

                        price=product.final_price,

                        quantity=item.quantity,

                        subtotal=item.subtotal,
                    )

                    # Reduce stock immediately only for COD
                    if order.payment_method == 'cod':
                        product.stock -= item.quantity
                        product.is_available = product.stock > 0

                        product.save(
                            update_fields=[
                                'stock',
                                'is_available',
                                'updated_at'
                            ]
                        )


            # Clear cart
            cart.items.all().delete()

            return redirect('my_orders')

    else:

        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'phone': request.user.phone,
        }

        form = CheckoutForm(
            initial=initial_data
        )


    subtotal = sum(
        item.subtotal for item in cart_items
    )

    delivery_fee = 40

    grand_total = subtotal + delivery_fee


    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'cart': cart,
            'delivery_fee': delivery_fee,
            'grand_total': grand_total,
        }
    )

@login_required
def my_orders(request):

    if request.user.role != 'customer':
        return redirect('shop_dashboard')

    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        'items'
    )

    return render(
        request,
        'orders/my_orders.html',
        {
            'orders': orders
        }
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    status_order = [
        'placed',
        'accepted',
        'preparing',
        'ready',
        'out_for_delivery',
        'delivered'
    ]

    current_status_index = -1

    if order.status in status_order:
        current_status_index = status_order.index(order.status)

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order,
            'status_order': status_order,
            'current_status_index': current_status_index,
        }
    )

@login_required
def cancel_order(request, order_id):
    if request.user.role != 'customer':
        return redirect('customer_dashboard')

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    if request.method == 'POST':

        # Customer can cancel only before preparation starts
        if order.status not in ['placed', 'accepted']:
            return redirect('order_detail', order_id=order.id)

        with transaction.atomic():

            # -------------------------------------------------
            # ONLINE PAYMENT + PAID
            # -------------------------------------------------
            if (
                order.payment_method == 'online'
                and order.payment_status == 'paid'
            ):
                payment = getattr(order, 'payment', None)

                if payment and payment.status == 'success':

                    # Create Razorpay refund
                    client = razorpay.Client(
                        auth=(
                            settings.RAZORPAY_KEY_ID,
                            settings.RAZORPAY_KEY_SECRET
                        )
                    )

                    try:
                        refund = client.payment.refund(
                            payment.razorpay_payment_id,
                            {
                                'amount': int(order.total_amount * 100),
                                'speed': 'normal',
                            }
                        )

                        payment.razorpay_refund_id = refund['id']
                        payment.refund_status = 'processed'
                        payment.save(
                            update_fields=[
                                'razorpay_refund_id',
                                'refund_status',
                                'updated_at'
                            ]
                        )

                    except Exception:
                        payment.refund_status = 'failed'
                        payment.save(
                            update_fields=[
                                'refund_status',
                                'updated_at'
                            ]
                        )

                        # Do not cancel if refund could not be created
                        return redirect(
                            'order_detail',
                            order_id=order.id
                        )

                    # Restore stock because online paid order
                    # had already deducted stock
                    for item in order.items.select_related('product'):
                        if item.product:
                            product = item.product
                            product.stock += item.quantity
                            product.is_available = True
                            product.save(
                                update_fields=[
                                    'stock',
                                    'is_available',
                                    'updated_at'
                                ]
                            )

            # -------------------------------------------------
            # COD ORDER
            # -------------------------------------------------
            elif order.payment_method == 'cod':

                # COD stock was deducted during checkout,
                # so restore it during cancellation.
                for item in order.items.select_related('product'):
                    if item.product:
                        product = item.product
                        product.stock += item.quantity
                        product.is_available = True
                        product.save(
                            update_fields=[
                                'stock',
                                'is_available',
                                'updated_at'
                            ]
                        )

            # -------------------------------------------------
            # ONLINE PAYMENT NOT PAID
            # -------------------------------------------------
            # No stock restoration and no refund is required
            # because stock was never deducted.

            order.status = 'cancelled'
            order.save(
                update_fields=[
                    'status',
                    'updated_at'
                ]
            )

            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                changed_by=request.user
            )

    return redirect('order_detail', order_id=order.id)


@login_required
def shop_orders(request):
    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if not shop:
        return redirect('shop_dashboard')

    orders = Order.objects.filter(
        shop=shop
    ).select_related(
        'customer'
    ).prefetch_related(
        'items'
    ).order_by('-created_at')

    return render(
        request,
        'orders/shop_orders.html',
        {
            'orders': orders,
        }
    )

@login_required
def update_order_status(request, order_id):
    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if not shop:
        return redirect('shop_dashboard')

    order = get_object_or_404(
        Order,
        id=order_id,
        shop=shop
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        allowed_transitions = {
            'placed': ['accepted'],
            'accepted': ['preparing'],
            'preparing': ['ready'],
            'ready': ['out_for_delivery'],
            'out_for_delivery': ['delivered'],
        }

        current_status = order.status

        # Prevent changes after cancellation or delivery
        if current_status in ['cancelled', 'delivered']:
            return redirect('shop_orders')

        # Check whether requested transition is valid
        if new_status in allowed_transitions.get(current_status, []):

            order.status = new_status
            order.save(
                update_fields=['status', 'updated_at']
            )

            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                changed_by=request.user
            )

            # Customer notification messages
            notification_messages = {
                'accepted': (
                    'Order Accepted',
                    f'Your order #{order.id} has been accepted by the shop.'
                ),

                'preparing': (
                    'Order Preparing',
                    f'Your order #{order.id} is now being prepared.'
                ),

                'ready': (
                    'Order Ready',
                    f'Your order #{order.id} is ready for pickup/delivery.'
                ),

                'out_for_delivery': (
                    'Out for Delivery',
                    f'Your order #{order.id} is out for delivery.'
                ),

                'delivered': (
                    'Order Delivered',
                    f'Your order #{order.id} has been delivered successfully.'
                ),
            }

            if new_status in notification_messages:

                title, message = notification_messages[new_status]

                Notification.objects.create(
                    customer=order.customer,
                    order=order,
                    title=title,
                    message=message
                )

    return redirect('shop_orders')

@login_required
def payment_page(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
        payment_method='online'
    )

    if order.payment_status == 'paid':
        return redirect(
            'order_detail',
            order_id=order.id
        )

    payment = get_object_or_404(
        Payment,
        order=order
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    # Create Razorpay Order only once
    if not payment.razorpay_order_id:

        razorpay_order = client.order.create({
            'amount': int(order.total_amount * 100),
            'currency': 'INR',
            'receipt': f'localkart_order_{order.id}',
        })

        payment.razorpay_order_id = razorpay_order['id']

        payment.save(
            update_fields=[
                'razorpay_order_id',
                'updated_at'
            ]
        )

    return render(
        request,
        'orders/payment.html',
        {
            'order': order,
            'payment': payment,
            'razorpay_order_id': payment.razorpay_order_id,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        }
    )

@login_required
def verify_payment(request):

    if request.method != 'POST':
        return JsonResponse(
            {
                'success': False,
                'message': 'Invalid request method.'
            },
            status=405
        )

    payment_id = request.POST.get(
        'razorpay_payment_id'
    )

    razorpay_order_id = request.POST.get(
        'razorpay_order_id'
    )

    signature = request.POST.get(
        'razorpay_signature'
    )

    if not payment_id or not razorpay_order_id or not signature:
        return JsonResponse(
            {
                'success': False,
                'message': 'Payment details are missing.'
            },
            status=400
        )

    payment = get_object_or_404(
        Payment,
        razorpay_order_id=razorpay_order_id,
        order__customer=request.user
    )

    order = payment.order

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:

        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })

        with transaction.atomic():

            # Prevent duplicate verification
            if payment.status == 'success' and order.payment_status == 'paid':
                return JsonResponse({
                    'success': True,
                    'order_id': order.id
                })

            payment.razorpay_payment_id = payment_id
            payment.status = 'success'

            payment.save(
                update_fields=[
                    'razorpay_payment_id',
                    'status',
                    'updated_at'
                ]
            )

            order.payment_status = 'paid'

            order.save(
                update_fields=[
                    'payment_status',
                    'updated_at'
                ]
            )

            # Deduct stock only after successful online payment
            for item in order.items.select_related('product'):

                if item.product:
                    product = item.product

                    product.stock -= item.quantity
                    product.is_available = product.stock > 0

                    product.save(
                        update_fields=[
                            'stock',
                            'is_available',
                            'updated_at'
                        ]
                    )

        return JsonResponse({
            'success': True,
            'order_id': order.id,
        })

    except razorpay.errors.SignatureVerificationError:

        payment.status = 'failed'

        payment.save(
            update_fields=[
                'status',
                'updated_at'
            ]
        )

        return JsonResponse(
            {
                'success': False,
                'message': 'Payment verification failed.'
            },
            status=400
        )

@login_required
def payment_result(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
        payment_method='online'
    )

    payment_success = (
        order.payment_status == 'paid'
    )

    return render(
        request,
        'orders/payment_result.html',
        {
            'order': order,
            'payment_success': payment_success,
        }
    )


@login_required
def notifications(request):
    if request.user.role != 'customer':
        return redirect('customer_dashboard')

    notifications = Notification.objects.filter(
        customer=request.user
    ).select_related(
        'order'
    ).order_by('-created_at')

    return render(
        request,
        'orders/notifications.html',
        {
            'notifications': notifications
        }
    )

@login_required
def mark_notification_read(request, notification_id):
    if request.user.role != 'customer':
        return redirect('customer_dashboard')

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        customer=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if notification.order:
        return redirect('order_detail', order_id=notification.order.id)

    return redirect('notifications')