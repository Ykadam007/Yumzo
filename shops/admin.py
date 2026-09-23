from django.contrib import admin
from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'owner',
        'city',
        'phone',
        'approval_status',
        'is_open',
        'created_at',
    )

    list_filter = (
        'approval_status',
        'is_open',
        'city',
    )

    search_fields = (
        'name',
        'owner__username',
        'phone',
        'city',
    )

    list_editable = (
        'approval_status',
    )