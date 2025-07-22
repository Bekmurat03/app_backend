# courier/services.py (НОВЫЙ ФАЙЛ)
from django.db import transaction
from rest_framework.exceptions import ValidationError
from orders.models import Order

@transaction.atomic
def accept_order_for_courier(order_id, courier):
    """
    Сервисная функция для безопасного назначения заказа на курьера.
    Предотвращает гонку состояний.
    """
    # Блокируем строку заказа в БД до конца транзакции.
    # Если другой курьер попытается принять этот же заказ, его запрос будет ждать,
    # а затем получит ошибку, так как статус заказа уже изменится.
    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != 'ready_for_pickup' or order.courier is not None:
        raise ValidationError("Этот заказ уже недоступен или взят другим курьером.")

    order.courier = courier
    order.status = 'on_the_way'
    order.save(update_fields=['courier', 'status'])
    
    # TODO: Отправить push-уведомление клиенту, что курьер выехал
    
    return order