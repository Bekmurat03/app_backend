# app_backend/apps/restaurants/admin.py (ТОЛЬКО АДМИН МЕНЯЕТ ТАРИФЫ)

from django.contrib import admin
from .models import Restaurant, DeliveryTariff


# Мы НЕ используем DeliveryTariffInline, чтобы рестораны не могли менять тарифы

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "address", "owner__phone")
    readonly_fields = ("created_at",)

    # Мы УБРАЛИ отсюда строку 'inlines = [DeliveryTariffInline]'

    # Ваша структура fieldsets остается без изменений
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "description", "address", "owner", "is_approved")
        }),
        ("Изображения", {
            "fields": ("logo", "banner")
        }),
        ("Категории", {
            "fields": ("categories",)
        }),
    )


# Этот раздел остаётся. Управлять тарифами можно будет только отсюда,
# и доступ сюда по умолчанию есть только у суперпользователя (администратора).
@admin.register(DeliveryTariff)
class DeliveryTariffAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'name', 'start_time', 'end_time', 'base_fee', 'fee_per_km')
    list_filter = ('restaurant',)
    search_fields = ('restaurant__name', 'name')