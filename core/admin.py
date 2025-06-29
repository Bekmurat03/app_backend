from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "role", "is_approved", "is_active", "is_staff")
    list_filter = ("role", "is_approved", "is_active")
    search_fields = ("username", "email")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Роли и доступ", {"fields": ("role", "is_approved")}),
    )
