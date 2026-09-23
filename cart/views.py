from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from products.models import Product

from .models import Cart, CartItem

@login_required
def add_to_cart(request, product_id):

    if request.user.role != 'customer':
        return redirect('shop_dashboard')

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
        stock__gt=0,
        shop__approval_status='approved'
    )

    quantity = 1

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        quantity = product.stock

    cart, created = Cart.objects.get_or_create(
        customer=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > product.stock:
            new_quantity = product.stock

        cart_item.quantity = new_quantity

    cart_item.save()

    return redirect('cart_detail')


@login_required
def cart_detail(request):

    if request.user.role != 'customer':
        return redirect('shop_dashboard')

    cart, created = Cart.objects.get_or_create(
        customer=request.user
    )

    items = cart.items.select_related(
        'product',
        'product__shop',
        'product__category'
    )

    return render(
        request,
        'cart/cart_detail.html',
        {
            'cart': cart,
            'items': items,
        }
    )


@login_required
def update_cart(request, item_id):

    if request.user.role != 'customer':
        return redirect('shop_dashboard')

    cart, created = Cart.objects.get_or_create(
        customer=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    if request.method == 'POST':

        quantity = int(
            request.POST.get(
                'quantity',
                1
            )
        )

        if quantity <= 0:

            item.delete()

        elif quantity <= item.product.stock:

            item.quantity = quantity
            item.save()

    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):

    if request.user.role != 'customer':
        return redirect('shop_dashboard')

    cart, created = Cart.objects.get_or_create(
        customer=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    if request.method == 'POST':

        item.delete()

    return redirect('cart_detail')