from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from accounts.models import CustomUser
from shops.models import Shop
from products.models import Product,Category
from orders.models import Order, OrderStatusHistory
from reviews.models import Review
from django.shortcuts import get_object_or_404
from django.db.models import Q,Sum



@login_required
def customer_dashboard(request):
    return render(request, 'dashboard/customer.html')


@login_required
def shop_dashboard(request):
    shop = getattr(request.user, 'shop', None)

    return render(
        request,
        'dashboard/shop.html',
        {
            'shop': shop,
        }
    )


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return render(
            request,
            'dashboard/access_denied.html'
        )

    total_users = CustomUser.objects.count()

    total_customers = CustomUser.objects.filter(
        role='customer'
    ).count()

    total_shop_owners = CustomUser.objects.filter(
        role='shop_owner'
    ).count()


    # ================= SHOPS =================

    total_shops = Shop.objects.count()

    pending_shops = Shop.objects.filter(
        approval_status='pending'
    ).count()

    approved_shops = Shop.objects.filter(
        approval_status='approved'
    ).count()


    # ================= PRODUCTS & ORDERS =================

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_reviews = Review.objects.count()


    # ================= ORDER STATUS =================

    placed_orders = Order.objects.filter(
        status='placed'
    ).count()

    accepted_orders = Order.objects.filter(
        status='accepted'
    ).count()

    preparing_orders = Order.objects.filter(
        status='preparing'
    ).count()

    ready_orders = Order.objects.filter(
        status='ready'
    ).count()

    out_for_delivery_orders = Order.objects.filter(
        status='out_for_delivery'
    ).count()

    delivered_orders = Order.objects.filter(
        status='delivered'
    ).count()

    cancelled_orders = Order.objects.filter(
        status='cancelled'
    ).count()


    # ================= PENDING ORDERS =================

    pending_orders = Order.objects.exclude(
        status__in=[
            'delivered',
            'cancelled'
        ]
    ).count()


    # ================= REVENUE =================

    total_revenue = Order.objects.filter(
        status='delivered'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0


    # ================= CONTEXT =================

    context = {

        # Users
        'total_users': total_users,
        'total_customers': total_customers,
        'total_shop_owners': total_shop_owners,

        # Shops
        'total_shops': total_shops,
        'pending_shops': pending_shops,
        'approved_shops': approved_shops,

        # Products
        'total_products': total_products,

        # Orders
        'total_orders': total_orders,
        'placed_orders': placed_orders,
        'accepted_orders': accepted_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
        'out_for_delivery_orders': out_for_delivery_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'pending_orders': pending_orders,

        # Reviews
        'total_reviews': total_reviews,

        # Revenue
        'total_revenue': total_revenue,
    }


    return render(
        request,
        'dashboard/admin_dashboard.html',
        context
    )

@login_required
def manage_shops(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    shops = Shop.objects.select_related('owner').order_by(
        'approval_status',
        '-created_at'
    )

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        shops = shops.filter(
            Q(name__icontains=search) |
            Q(owner__username__icontains=search) |
            Q(owner__email__icontains=search)
        )

    if status:
        shops = shops.filter(approval_status=status)

    paginator = Paginator(shops, 10)

    page_number = request.GET.get('page')

    shops = paginator.get_page(page_number)

    return render(
        request,
        'dashboard/manage_shops.html',
        {
            'shops': shops,
            'search': search,
            'selected_status': status,
        }
    )


@login_required
def approve_shop(request, shop_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    shop = get_object_or_404(Shop, id=shop_id)

    if request.method == 'POST':
        shop.approval_status = 'approved'
        shop.rejection_reason = ''
        shop.save(update_fields=[
            'approval_status',
            'rejection_reason',
            'updated_at',
        ])

    return redirect('manage_shops')

@login_required
def reject_shop(request, shop_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    shop = get_object_or_404(Shop, id=shop_id)

    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', '').strip()

        shop.approval_status = 'rejected'
        shop.rejection_reason = reason
        shop.save(update_fields=[
            'approval_status',
            'rejection_reason',
            'updated_at',
        ])

    return redirect('manage_shops')

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    users = CustomUser.objects.all().order_by('-date_joined')

    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', '').strip()

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if role:
        users = users.filter(role=role)

    paginator = Paginator(users, 10)

    page_number = request.GET.get('page')

    users = paginator.get_page(page_number)

    return render(
        request,
        'dashboard/manage_users.html',
        {
            'users': users,
            'search': search,
            'selected_role': role,
        }
    )

@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    user = get_object_or_404(CustomUser, id=user_id)

    # Prevent admin from disabling their own account
    if user == request.user:
        return redirect('manage_users')

    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

    return redirect('manage_users')

@login_required
def manage_products(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    products = Product.objects.select_related(
        'shop',
        'category'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(shop__name__icontains=search)
        )

    if category:
        products = products.filter(
            category_id=category
        )

    categories = Category.objects.filter(
        is_active=True
    ).order_by('name')

    paginator = Paginator(products, 10)

    page_number = request.GET.get('page')

    products = paginator.get_page(page_number)

    return render(
        request,
        'dashboard/manage_products.html',
        {
            'products': products,
            'categories': categories,
            'search': search,
            'selected_category': category,
        }
    )


@login_required
def toggle_product(request, product_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.is_available = not product.is_available
        product.save(update_fields=['is_available'])

    return redirect('manage_products')


@login_required
def delete_product_admin(request, product_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()

    return redirect('manage_products')

@login_required
def edit_product_admin(request, product_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.description = request.POST.get('description', '').strip()
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock')
        product.category_id = request.POST.get('category')

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.is_available = 'is_available' in request.POST

        product.save()

        return redirect('manage_products')

    categories = Category.objects.filter(
        is_active=True
    ).order_by('name')

    return render(
        request,
        'dashboard/edit_product_admin.html',
        {
            'product': product,
            'categories': categories,
        }
    )

@login_required
def manage_orders(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    orders = Order.objects.select_related(
        'customer',
        'shop',
        'payment'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()
    payment_method = request.GET.get('payment_method', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if search:
        orders = orders.filter(
            Q(customer__username__icontains=search) |
            Q(customer__email__icontains=search) |
            Q(shop__name__icontains=search)
        )

    if status:
        orders = orders.filter(status=status)

    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    if payment_method:
        orders = orders.filter(payment_method=payment_method)

    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)

    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')

    orders = paginator.get_page(page_number)

    return render(
        request,
        'dashboard/manage_orders.html',
        {
            'orders': orders,
            'search': search,
            'selected_status': status,
            'selected_payment_status': payment_status,
            'selected_payment_method': payment_method,
            'date_from': date_from,
            'date_to': date_to,
            'status_choices': Order.STATUS_CHOICES,
            'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
            'payment_method_choices': Order.PAYMENT_CHOICES,
        }
    )


@login_required
def admin_order_detail(request, order_id):
    if not request.user.is_superuser:
        return render(
            request,
            'dashboard/access_denied.html'
        )

    order = get_object_or_404(
        Order.objects.select_related(
            'customer',
            'shop',
            'payment'
        ).prefetch_related(
            'items',
            'status_history'
        ),
        id=order_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('status', '').strip()

        valid_statuses = dict(Order.STATUS_CHOICES)

        if new_status in valid_statuses:

            # Only create history when status actually changes
            if order.status != new_status:

                order.status = new_status
                order.save(update_fields=[
                    'status',
                    'updated_at',
                ])

                OrderStatusHistory.objects.create(
                    order=order,
                    status=new_status,
                    changed_by=request.user
                )

        return redirect(
            'admin_order_detail',
            order_id=order.id
        )

    return render(
        request,
        'dashboard/admin_order_detail.html',
        {
            'order': order,
            'status_choices': Order.STATUS_CHOICES,
            'status_history': order.status_history.all(),
        }
    )

@login_required
def manage_reviews(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    reviews = Review.objects.select_related(
        'customer',
        'shop'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    rating = request.GET.get('rating', '').strip()

    if search:
        reviews = reviews.filter(
            Q(customer__username__icontains=search) |
            Q(shop__name__icontains=search) |
            Q(comment__icontains=search)
        )

    if rating:
        reviews = reviews.filter(rating=rating)

    paginator = Paginator(reviews, 10)

    page_number = request.GET.get('page')

    reviews = paginator.get_page(page_number)

    return render(
        request,
        'dashboard/manage_reviews.html',
        {
            'reviews': reviews,
            'search': search,
            'selected_rating': rating,
        }
    )

@login_required
def delete_review(request, review_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        review.delete()

    return redirect('manage_reviews')

@login_required
def manage_categories(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    categories = Category.objects.all().order_by('name')

    search = request.GET.get('search', '').strip()

    if search:
        categories = categories.filter(name__icontains=search)

    return render(
        request,
        'dashboard/manage_categories.html',
        {
            'categories': categories,
            'search': search,
        }
    )


@login_required
def add_category(request):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if name:
            Category.objects.create(
                name=name,
                is_active=True
            )

        return redirect('manage_categories')

    return render(request, 'dashboard/add_category.html')


@login_required
def edit_category(request, category_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if name:
            category.name = name
            category.save(update_fields=['name'])

        return redirect('manage_categories')

    return render(
        request,
        'dashboard/edit_category.html',
        {'category': category}
    )


@login_required
def toggle_category(request, category_id):
    if not request.user.is_superuser:
        return render(request, 'dashboard/access_denied.html')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.is_active = not category.is_active
        category.save(update_fields=['is_active'])

    return redirect('manage_categories')




