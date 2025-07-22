from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import PromoBanner, PromoCode
from .serializers import PromoBannerSerializer, PromoCodeSerializer
from . import services 
from orders.models import Order
from orders.permissions import IsClientOwnerOfOrder 

class PromoBannerListView(generics.ListAPIView):
    """
    Возвращает список активных промо-баннеров для главного экрана.
    """
    queryset = PromoBanner.objects.filter(is_active=True)
    serializer_class = PromoBannerSerializer
    permission_classes = [permissions.AllowAny]


class ValidatePromoCodeView(APIView):
    """
    Проверяет, существует ли промокод и валиден ли он (не истек, не превышен лимит и т.д.).
    Именно этот View используется вашим Flutter-приложением на экране оформления заказа.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code = request.data.get("code", "").strip().upper() # Приводим код к верхнему регистру для надежности
        try:
            # Используем менеджер модели или метод для проверки валидности
            # (предполагается, что is_valid() проверяет дату и лимиты)
            promo = PromoCode.objects.get(code__iexact=code)
            
            if not promo.is_valid():
                return Response({"error": "Промокод недействителен или истек."}, status=status.HTTP_400_BAD_REQUEST)

            # Если все в порядке, возвращаем данные о промокоде
            serializer = PromoCodeSerializer(promo)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except PromoCode.DoesNotExist:
            return Response({"error": "Промокод не найден"}, status=status.HTTP_404_NOT_FOUND)


class ApplyPromoCodeView(APIView):
    """
    Применяет промокод к УЖЕ СУЩЕСТВУЮЩЕМУ заказу.
    (В нашей текущей логике Flutter не используется, но может пригодиться в будущем).
    """
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]

    def post(self, request, *args, **kwargs):
        code = request.data.get("code", "").strip()
        order_id = request.data.get("order_id")

        if not code or not order_id:
            return Response({"error": "Необходимы code и order_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = get_object_or_404(Order, id=order_id)
            # Проверяем, что пользователь является владельцем заказа
            self.check_object_permissions(request, order)
            
            # Вызываем сервис, который сделает всю сложную работу
            updated_order, discount_amount = services.apply_promo_code_to_order(code, order)
            
            from orders.serializers import OrderSerializer # Локальный импорт для избежания циклических зависимостей
            return Response({
                'message': f'Промокод успешно применен! Скидка: {discount_amount}',
                'order': OrderSerializer(updated_order).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)