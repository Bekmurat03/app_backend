from django.contrib import admin
from .models import PaymentCard, TokenizationAttempt

@admin.register(PaymentCard)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'card_type', 'last_four', 'is_primary')
    list_filter = ('card_type', 'is_primary')
    search_fields = ('user__phone',)

@admin.register(TokenizationAttempt)
class TokenizationAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__phone',)
    readonly_fields = ('id', 'user', 'created_at', 'paylink_checkout_token')