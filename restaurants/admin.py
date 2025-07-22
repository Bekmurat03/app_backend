# restaurants/admin.py

from django.contrib import admin
from .models import Restaurant, DeliveryTariff

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    # 👇 ИСПРАВЛЕНИЕ: Заменяем 'robokassa_shop_code' на 'robokassa_login'
    list_display = ("id", "name", "owner", "robokassa_login", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "address", "owner__phone")
    readonly_fields = ("created_at", "average_rating", "review_count")

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "owner", "description", "address", "phone_number")
        }),
        ("Статус", {
            "fields": ("is_approved", "is_active")
        }),
        ("Финансы", {
            # 👇 ИСПРАВЛЕНИЕ: Заменяем 'robokassa_shop_code' на 'robokassa_login'
            "fields": ("robokassa_login", "average_rating", "review_count")
        }),
        ("Изображения", {
            "fields": ("logo", "banner")
        }),
        ("Геопозиция", {
            "fields": ("latitude", "longitude")
        }),
        ("Категории", {
            "fields": ("categories",)
        }),
        ("Даты", {
            "fields": ("created_at",)
        }),
    )

@admin.register(DeliveryTariff)
class DeliveryTariffAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'name', 'start_time', 'end_time', 'base_fee', 'fee_per_km')
    list_filter = ('restaurant',)
    search_fields = ('restaurant__name', 'name')