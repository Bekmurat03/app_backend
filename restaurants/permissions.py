# restaurants/permissions.py (НОВЫЙ ФАЙЛ)

from rest_framework.permissions import BasePermission
from .models import Restaurant

class IsRestaurantOwner(BasePermission):
    """
    Правило доступа, которое разрешает действия только владельцу ресторана.
    """
    message = "У вас нет прав для управления этим рестораном."

    def has_object_permission(self, request, view, obj):
        # `obj` здесь - это экземпляр ресторана (Restaurant).
        # Мы просто проверяем, совпадает ли владелец объекта с текущим пользователем.
        return obj.owner == request.user