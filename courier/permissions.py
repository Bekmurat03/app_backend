# app_backend/apps/courier/permissions.py (НОВЫЙ ФАЙЛ)
from rest_framework.permissions import BasePermission

class IsCourier(BasePermission):
    """
    Пользовательское правило доступа.
    Пропускает только пользователей с ролью 'courier'.
    """
    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован и его роль - курьер
        return request.user and request.user.is_authenticated and request.user.role == 'courier'