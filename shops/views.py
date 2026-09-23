from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Shop
from .forms import ShopForm
from django.db.models import Avg, Count


@login_required
def create_shop(request):

    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    if hasattr(request.user, 'shop'):
        return redirect('shop_profile')

    if request.method == 'POST':

        form = ShopForm(request.POST)

        if form.is_valid():

            shop = form.save(commit=False)

            shop.owner = request.user

            shop.save()

            return redirect('shop_profile')

    else:

        form = ShopForm()

    return render(
        request,
        'shops/create_shop.html',
        {
            'form': form
        }
    )


@login_required
def shop_profile(request):

    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = request.user.shop

    return render(
        request,
        'shops/shop_profile.html',
        {
            'shop': shop
        }
    )


def shop_list(request):

    shops = Shop.objects.filter(
        approval_status='approved'
    ).annotate(
        review_count=Count('reviews'),
        average_review_rating=Avg('reviews__rating')
    ).order_by('-rating', 'name')

    return render(
        request,
        'shops/shop_list.html',
        {
            'shops': shops
        }
    )
