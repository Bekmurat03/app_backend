# promos/services.py (НОВЫЙ ФАЙЛ)

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from orders.models import Order
from .models import PromoCode

@transaction.atomic
def apply_promo_code_to_order(promo_code_str: str, order: Order):
    """
    Применяет промокод к заказу.
    - Проверяет валидность промокода.
    - Проверяет, не был ли он уже применен.
    - Пересчитывает стоимость заказа.
    - Помечает промокод как использованный.
    Все операции выполняются в рамках одной транзакции.
    """
    if order.promo_code:
        raise ValidationError("К этому заказу уже применен промокод.")
    
    if order.is_paid:
        raise ValidationError("Нельзя применить промокод к уже оплаченному заказу.")

    try:
        # Блокируем строку промокода, чтобы избежать гонки состояний
        promo_code = PromoCode.objects.select_for_update().get(code__iexact=promo_code_str)
    except PromoCode.DoesNotExist:
        raise ValidationError("Промокод не найден.")

    if not promo_code.is_valid():
        raise ValidationError("Срок действия промокода истек или он больше недействителен.")

    # Вычисляем скидку
    discount_amount = (order.total_price * promo_code.discount) / 100
    
    # Применяем скидку, но не даем цене уйти в минус
    order.total_price = max(0, order.total_price - discount_amount)
    order.promo_code = promo_code # Сохраняем связь
    
    # Атомарно увеличиваем счетчик использования
    promo_code.apply() 
    
    order.save()

    return order, discount_amount