from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'is_active',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'shop',
        'category',
        'price',
        'discount_price',
        'stock',
        'is_available',
        'created_at',
    )

    list_filter = (
        'category',
        'is_available',
    )

    search_fields = (
        'name',
        'shop__name',
    )