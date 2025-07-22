# orders/permissions.py (НОВЫЙ ФАЙЛ)

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsClientOwnerOfOrder(BasePermission):
    """
    Разрешает доступ только клиенту, который создал заказ.
    """
    message = "У вас нет прав для просмотра или изменения этого заказа."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsRestaurantOwnerOfOrder(BasePermission):
    """
    Разрешает доступ только владельцу ресторана, к которому относится заказ.
    """
    message = "Этот заказ не относится к вашему ресторану."

    def has_object_permission(self, request, view, obj):
        # Проверяем, что у пользователя есть ресторан и заказ принадлежит ему
        return hasattr(request.user, 'restaurants') and obj.restaurant in request.user.restaurants.all()