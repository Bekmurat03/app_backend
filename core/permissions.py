# core/permissions.py

from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Правило доступа, которое разрешает доступ только владельцу объекта.
    Предполагается, что у модели есть поле 'user'.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ, если поле 'user' объекта совпадает с пользователем,
        # который делает запрос.
        return obj.user == request.user