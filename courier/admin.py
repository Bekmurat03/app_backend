# courier/admin.py
from django.contrib import admin
from .models import CourierProfile

@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('user__phone', 'user__first_name')
    # Делаем поле статуса редактируемым прямо в списке
    list_editable = ('verification_status',)