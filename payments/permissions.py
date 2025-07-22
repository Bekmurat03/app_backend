# payments/permissions.py (НОВЫЙ ФАЙЛ)
from rest_framework.permissions import BasePermission

class IsCardOwner(BasePermission):
    message = 'Вы можете управлять только своими картами.'
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user