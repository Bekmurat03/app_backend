from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "address", "owner__phone")
    readonly_fields = ("created_at",)

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
