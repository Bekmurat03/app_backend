# courier/permissions.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework.permissions import BasePermission

class IsCourier(BasePermission):
    """
    Пользовательское правило доступа.
    Пропускает только пользователей с ролью 'courier'.
    """
    message = "Это действие доступно только для курьеров."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'courier'


class IsOrderCourier(BasePermission):
    """
    Правило доступа, которое разрешает действия только курьеру,
    назначенному на данный заказ.
    """
    message = "Вы не назначены на этот заказ."

    def has_object_permission(self, request, view, obj):
        # obj здесь - это экземпляр Order
        return obj.courier == request.user