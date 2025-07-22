# reviews/permissions.py (НОВЫЙ ФАЙЛ)
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsReviewOwner(BasePermission):
    """
    Разрешает доступ к объекту Review только его автору.
    """
    message = "Вы можете управлять только своими отзывами."

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in SAFE_METHODS:
            return True
        # Для остальных методов (PUT, PATCH, DELETE) проверяем авторство
        return obj.user == request.user