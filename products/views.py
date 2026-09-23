from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import ProductForm
from .models import Product,Category



@login_required
def add_product(request):

    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if shop is None:
        return redirect('create_shop')

    if shop.approval_status != 'approved':
        return redirect('shop_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():

            product = form.save(commit=False)

            product.shop = shop

            product.save()

            return redirect('product_list')

    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {
        'form': form,
        'shop': shop,
    })

@login_required
def product_list(request):
    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if shop is None:
        return redirect('create_shop')

    if shop.approval_status != 'approved':
        return redirect('shop_dashboard')

    products = Product.objects.filter(
        shop=shop
    ).select_related('category').order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products,
        'shop': shop,
    })


@login_required
def edit_product(request, product_id):

    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if shop is None:
        return redirect('create_shop')

    if shop.approval_status != 'approved':
        return redirect('shop_dashboard')

    product = get_object_or_404(
        Product,
        id=product_id,
        shop=shop
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect('product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
        'shop': shop,
    })


@login_required
def delete_product(request, product_id):

    if request.user.role != 'shop_owner':
        return redirect('customer_dashboard')

    shop = getattr(request.user, 'shop', None)

    if shop is None:
        return redirect('create_shop')

    if shop.approval_status != 'approved':
        return redirect('shop_dashboard')

    product = get_object_or_404(
        Product,
        id=product_id,
        shop=shop
    )

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(request, 'products/delete_product.html', {
        'product': product,
        'shop': shop,
    })

def marketplace(request):

    products = Product.objects.filter(
        is_available=True,
        stock__gt=0,
        shop__approval_status='approved'
    ).select_related(
        'shop',
        'category'
    ).prefetch_related(
        'reviews'
    )

    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    # Search
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search) |
            Q(shop__name__icontains=search)
        )

    # Category filter
    if category:
        products = products.filter(
            category_id=category,
            category__is_active=True
        )

    categories = Category.objects.filter(
        is_active=True
    ).order_by('name')

    return render(
        request,
        'products/marketplace.html',
        {
            'products': products,
            'categories': categories,
            'search': search,
            'selected_category': category,
        }
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related(
            'shop',
            'category'
        ).prefetch_related(
            'reviews__customer'
        ),
        id=product_id,
        is_available=True,
        stock__gt=0,
        shop__approval_status='approved'
    )

    reviews = product.reviews.select_related(
        'customer'
    ).order_by('-created_at')

    review_count = reviews.count()

    if review_count > 0:
        average_rating = sum(
            review.rating for review in reviews
        ) / review_count
    else:
        average_rating = 0

    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'review_count': review_count,
            'average_rating': average_rating,
        }
    )


def shop_products(request, shop_id):
    from shops.models import Shop

    shop = get_object_or_404(
        Shop,
        id=shop_id,
        approval_status='approved'
    )

    products = Product.objects.filter(
        shop=shop,
        is_available=True,
        stock__gt=0
    ).select_related(
        'category'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    if category:
        products = products.filter(
            category_id=category
        )

    categories = Category.objects.filter(
        is_active=True,
        products__shop=shop
    ).distinct().order_by('name')

    return render(
        request,
        'products/shop_products.html',
        {
            'shop': shop,
            'products': products,
            'categories': categories,
            'search': search,
            'selected_category': category,
        }
    )