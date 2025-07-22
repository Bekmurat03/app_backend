# menu/permissions.py (НОВЫЙ ФАЙЛ)

from rest_framework.permissions import BasePermission

class IsDishOwner(BasePermission):
    """
    Разрешает доступ к объекту Dish только владельцу ресторана,
    которому принадлежит это блюдо.
    """
    message = "У вас нет прав для управления этим блюдом."

    def has_object_permission(self, request, view, obj):
        # obj здесь - это экземпляр Dish
        # Проверяем, что у пользователя есть рестораны и
        # что ресторан блюда принадлежит текущему пользователю.
        if request.user.is_authenticated and hasattr(request.user, 'restaurants'):
            return obj.restaurant in request.user.restaurants.all()
        return False