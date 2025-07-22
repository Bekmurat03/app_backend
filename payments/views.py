from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import uuid

# Наши модели и сервисы
from .models import SavedUserCard
from orders.models import Order, OrderItem
from core.models import Address
from promos.models import PromoCode
from .services import PayLinkService 

# Наши сериализаторы
from .serializers import SavedUserCardSerializer
# 👇 ИСПРАВЛЯЕМ ИМПОРТ: используем правильное имя класса
from orders.serializers import CreateOrderSerializer 


class CreateOrderAndPaymentView(APIView):
    """
    Главная view для оформления заказа.
    Она создает заказ в БД и возвращает ссылку на оплату.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # 👇 ИСПРАВЛЯЕМ ИМЯ КЛАССА ЗДЕСЬ
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Ваш CreateOrderSerializer уже делает всю работу по созданию заказа
        # и расчету суммы, поэтому мы просто вызываем его метод save().
        order = serializer.save()

        # --- Создание платежа через PayLink ---
        try:
            paylink_service = PayLinkService()
            payment_url = paylink_service.create_payment(
                amount=float(order.total_price),
                order_id=str(order.id),
                description=f"Оплата заказа №{order.id}",
                # enable_apple_pay и enable_google_pay теперь внутри сервиса
            )
            return Response({"payment_url": payment_url}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Если оплата не удалась, откатываем создание заказа
            transaction.set_rollback(True)
            return Response({"error": f"Ошибка создания платежа: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SavedCardListView(generics.ListAPIView):
    """
    Возвращает список сохраненных карт пользователя.
    """
    serializer_class = SavedUserCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedUserCard.objects.filter(user=self.request.user)


class PayLinkWebhookView(APIView):
    """
    Принимает уведомления от PayLink об успешной оплате или сохранении карты.
    """
    def post(self, request, *args, **kwargs):
        # ВАЖНО: здесь должна быть логика проверки подписи запроса от PayLink
        event_type = request.data.get("type")
        data = request.data.get("data")

        if event_type == "payment.success":
            order_id = data.get("order_id")
            # Находим заказ в нашей БД и помечаем его как оплаченный
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'PAID' # или ваш статус 'Оплачен'
                order.save()
            except Order.DoesNotExist:
                pass # Игнорируем или логируем ошибку

        elif event_type == "card.tokenized":
            user_id = data.get("user_id")
            card_token = data.get("token")
            card_mask = data.get("mask")
            # Сохраняем новую карту для пользователя
            if user_id and card_token and card_mask:
                SavedUserCard.objects.create(
                    user_id=user_id,
                    card_token=card_token,
                    card_mask=card_mask
                )

        return Response(status=status.HTTP_200_OK)