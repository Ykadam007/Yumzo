from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'accounts/',
        include('accounts.urls')
    ),

    path(
        'dashboard/',
        include('dashboard.urls')
    ),

    path(
        'shops/',
        include('shops.urls')
    ),

    path(
        'products/',
        include('products.urls')
    ),

    path(
        'cart/',
        include('cart.urls')
    ),

    path('orders/', include('orders.urls')),

    path('reviews/', include('reviews.urls')),


]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)