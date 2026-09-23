from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg

from .forms import ReviewForm
from .models import Review
from orders.models import Order
from products.models import Product


@login_required
def add_review(request, order_id, product_id):
    if request.user.role != 'customer':
        return redirect('customer_dashboard')

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
        status='delivered'
    )

    product = get_object_or_404(Product, id=product_id)

    # Make sure the customer actually purchased this product
    get_object_or_404(
        order.items,
        product=product
    )

    review = Review.objects.filter(
        customer=request.user,
        product=product,
        order=order
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            review = form.save(commit=False)

            review.customer = request.user
            review.product = product
            review.shop = order.shop
            review.order = order

            review.save()

            # Update shop's average rating
            shop_rating = Review.objects.filter(
                shop=order.shop
            ).aggregate(
                average=Avg('rating')
            )['average']

            if shop_rating is not None:
                order.shop.rating = round(float(shop_rating), 2)
                order.shop.save(
                    update_fields=['rating']
                )

            return redirect(
                'order_detail',
                order_id=order.id
            )

    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        'reviews/add_review.html',
        {
            'form': form,
            'product': product,
            'order': order,
            'review': review,
        }
    )