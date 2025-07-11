# orders/views.py (ФИНАЛЬНАЯ И ИСПРАВЛЕННАЯ ВЕРСИЯ)

import logging
import traceback
import requests
import base64
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import services as order_services
from .models import Order
from .permissions import IsClientOwnerOfOrder, IsRestaurantOwnerOfOrder
from .serializers import OrderSerializer, OrderCreateSerializer
from payments.models import PaymentCard # Убедитесь, что это правильный путь импорта
from payments.services import PayLinkService # 👈 Импортируем наш сервис
from rest_framework.exceptions import ValidationError

from core.models import Address, User # 👈 импортируем User
from rest_framework.exceptions import ValidationError, APIException

logger = logging.getLogger(__name__)


# --- VIEWS ДЛЯ КЛИЕНТА ---

class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'restaurant'
        ).prefetch_related(
            'items__menu'
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data['items']
        address_id = serializer.validated_data['address_id']
        comment = serializer.validated_data.get('comment', '')

        try:
            order = order_services.create_order_with_calculations(request.user, items_data, address_id, comment)
            
            card = PaymentCard.objects.filter(user=request.user, is_primary=True).first()
            if not card:
                raise ValidationError("У вас нет основной карты для оплаты.")
            
            payment_service = PayLinkService()
            payment_service.authorize_payment(order, card)

            full_serializer = OrderSerializer(order)
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(generics.RetrieveAPIView):
    """
    Для клиента: получение деталей одного конкретного заказа.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]
    queryset = Order.objects.select_related('restaurant').prefetch_related('items__menu').all()


class CancelOrderView(APIView):
    """
    Для клиента: отмена своего заказа.
    """
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
        self.check_object_permissions(request, order)

        if order.status == 'pending':
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            
            # Если заказ был оплачен, инициируем возврат
            if order.is_paid and order.payment_id:
                # В реальном проекте вызов возврата лучше делать асинхронной задачей (через Celery)
                # Здесь для простоты вызываем напрямую.
                refund_successful = self._refund_payment(order)
                if not refund_successful:
                    # Если возврат не удался, нужно уведомить администратора
                    logger.error(f"Не удалось выполнить автоматический возврат для отмененного заказа {order.id}")
                    # Можно оставить заказ в статусе 'cancellation_requested' для ручной обработки
            
            return Response({'status': 'Заказ успешно отменен'}, status=status.HTTP_200_OK)

        return Response({'error': 'Этот заказ уже нельзя отменить.'}, status=status.HTTP_400_BAD_REQUEST)

    def _refund_payment(self, order):
        """ Вспомогательный метод для выполнения возврата. """
        # Эта логика дублирует RefundPaymentView, в идеале ее нужно вынести в сервисный слой
        headers = {"Authorization": f"Bearer {settings.PAYLINK_API_SECRET}"}
        payload = {"amount": int(order.total_price * 100)}
        try:
            response = requests.post(
                f"https://api.paylink.kz/api/v1/payments/{order.payment_id}/refund",
                json=payload, headers=headers, timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса возврата к PayLink для заказа {order.id}: {str(e)}")
            return False

# --- VIEWS ДЛЯ РЕСТОРАНА ---

class RestaurantOrderListView(generics.ListAPIView):
    """
    Для ресторана: просмотр всех заказов, которые к нему относятся.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'restaurants') or not self.request.user.restaurants.exists():
            return Order.objects.none()
        restaurant = self.request.user.restaurants.first()
        return Order.objects.filter(restaurant=restaurant).select_related('user').prefetch_related('items__menu').order_by('-created_at')


class RestaurantManageOrderView(APIView):
    """
    Единый view для управления заказом рестораном.
    """
    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwnerOfOrder]

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
        self.check_object_permissions(request, order)

        action = request.data.get('action')
        
        # ... (остальная логика управления заказом остается прежней) ...

        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- VIEWS ДЛЯ ПЛАТЕЖЕЙ ---

class CreatePaymentView(APIView):
    """
    Создает платеж через PayLink.
    """
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        self.check_object_permissions(request, order)

        if order.is_paid:
            return Response({'error': 'Этот заказ уже оплачен.'}, status=status.HTTP_400_BAD_REQUEST)

        # Сумма в тиынах, минимальная сумма для многих шлюзов - 100 тг (10000 тиын)
        amount_in_tiyn = max(int(order.total_price * 100), 10000) 
        credentials = f"{settings.PAYLINK_API_KEY}:{settings.PAYLINK_API_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "X-API-Version": "2"
        }

        payload = {
            "checkout": {
                "transaction_type": "payment",
                "order": {
                    "id": str(order.id), # Отправляем наш ID заказа
                    "amount": amount_in_tiyn,
                    "currency": "KZT",
                    "description": f"Оплата заказа №{order.code} в JetFood"
                },
                "settings": {
                    "success_url": "jetfood://payment/success",
                    "failure_url": "jetfood://payment/failure"
                },
                # ... (остальные поля payload из вашего оригинального кода) ...
            }
        }
        
        try:
            response = requests.post("https://checkout.paylink.kz/ctp/api/checkouts", json=payload, headers=headers, timeout=15)
            response.raise_for_status() # Вызовет ошибку для плохих статусов (4xx, 5xx)
            response_data = response.json()
            
            # Сохраняем ID платежа, чтобы связать его с заказом
            order.payment_id = response_data.get('id')
            order.save(update_fields=['payment_id'])
            
            return Response({"payment_url": response_data['checkout']['redirect_url']})
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к PayLink при создании платежа для заказа {order.id}: {str(e)}")
            return Response({'error': 'Ошибка при создании платежа. Попробуйте позже.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayLinkWebhookView(APIView):
    """Принимает и обрабатывает уведомления (вебхуки) от PayLink."""
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        logger.info(f"Получен вебхук от PayLink: {data}")
        
        transaction_data = data.get('transaction', {})
        payment_status = transaction_data.get('status')
        order_id_str = transaction_data.get('tracking_id') # Используем tracking_id, если он есть
        
        if payment_status != 'successful':
            return Response(status=status.HTTP_200_OK)

        # РАЗДЕЛЯЕМ ЛОГИКУ ПО НАЛИЧИЮ ДАННЫХ КАРТЫ
        if 'credit_card' in transaction_data and transaction_data['credit_card'].get('token'):
            # Это вебхук от микро-платежа для сохранения карты
            try:
                service = PayLinkService()
                service.process_tokenization_webhook(data)
            except Exception as e:
                logger.error(f"Критическая ошибка при обработке вебхука токенизации: {traceback.format_exc()}")
        elif order_id_str:
            # Это вебхук от оплаты обычного заказа
            self.handle_payment_webhook(data, order_id_str)
        
        return Response({"status": "ok, webhook processed"}, status=status.HTTP_200_OK)

    # Вспомогательная функция для обработки оплаты обычного заказа (без изменений)
    def handle_payment_webhook(self, data: dict, order_id: str):
        try:
            order = Order.objects.select_for_update().get(id=order_id)
            if order.is_paid:
                return

            order.is_paid = True
            order.payment_id = data.get('uid')
            if order.status == 'pending':
                order.status = 'accepted'
            
            order.save(update_fields=['is_paid', 'payment_id', 'status'])
        except Order.DoesNotExist:
            logger.error(f"Получен вебхук для несуществующего заказа с ID {order_id}.")


class RefundPaymentView(APIView):
    """
    Выполняет возврат платежа через PayLink.
    """
    permission_classes = [permissions.IsAuthenticated] # Можно ограничить доступ администраторам

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        # TODO: Добавить проверку прав (например, только админ может делать возврат)

        if not order.is_paid or not order.payment_id:
            return Response({'error': 'Этот заказ не был оплачен или не имеет ID платежа.'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {settings.PAYLINK_API_SECRET}"}
        payload = {"amount": int(order.total_price * 100)}

        try:
            response = requests.post(f"https://api.paylink.kz/api/v1/payments/{order.payment_id}/refund", json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Обновляем статус заказа после успешного возврата
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            
            return Response({'success': True, 'message': 'Возврат успешно выполнен.'})
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к PayLink при возврате для заказа {order.id}: {str(e)}")
            return Response({'error': 'Ошибка при возврате платежа.'}, status=response.status_code if 'response' in locals() else 500)
class PayOrderView(APIView):
    """Проводит оплату заказа с помощью сохраненной карты."""
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        self.check_object_permissions(request, order) # Проверяем, что это заказ пользователя

        if order.is_paid:
            return Response({'error': 'Этот заказ уже оплачен.'}, status=status.HTTP_400_BAD_REQUEST)

        card_id = request.data.get('card_id')
        if not card_id:
            return Response({'error': 'Необходимо указать ID карты для оплаты (card_id).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
        except PaymentCard.DoesNotExist:
             return Response({'error': 'Указанная карта не найдена или не принадлежит вам.'}, status=status.HTTP_404_NOT_FOUND)

        service = PayLinkService()
        try:
            payment_data = service.charge_saved_card(order, card)
            # Возвращаем обновленный заказ
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Логируем ошибку и возвращаем понятный ответ
            logger.error(f"Ошибка оплаты заказа {order.id} картой {card.id}: {str(e)}")
            return Response({"error": "Не удалось провести платеж. Попробуйте другую карту или повторите позже."}, status=status.HTTP_400_BAD_REQUEST)
class CalculateOrderTotalsView(APIView):
    """Рассчитывает и возвращает все стоимости для заказа БЕЗ его создания."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items_data = serializer.validated_data['items']
        address_id = serializer.validated_data['address_id']
        try:
            address_obj = get_object_or_404(Address, id=address_id, user=request.user)
            totals = order_services.calculate_order_totals(items_data, address_obj)
            return Response(totals, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.detail[0] if isinstance(e.detail, list) else str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)


class CreateOrderView(APIView):
    """
    Для клиента: 1. Создает заказ со всеми расчетами. 2. Возвращает ссылку на оплату.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']
        address_id = serializer.validated_data['address_id']
        card_id = serializer.validated_data.get('card_id')
        comment = serializer.validated_data.get('comment', '')

        if not card_id:
            return Response({"error": "Необходимо выбрать карту для оплаты."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = order_services.create_order_with_calculations(request.user, items_data, address_id, comment)
                card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
                payment_service = PayLinkService()
                payment_data = payment_service.create_payment_url_for_order(order, card)

            response_data = OrderSerializer(order).data
            response_data['payment_info'] = payment_data
            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.detail[0] if isinstance(e.detail, list) else str(e.detail)},
                            status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            return Response({"error": f"Ошибка платежной системы: {e.detail}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при создании заказа: {traceback.format_exc()}")
            return Response({"error": "Произошла внутренняя ошибка на сервере."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateAndPayOrderView(APIView):
    """
    Для клиента: 1. Создает заказ. 2. Сразу же проводит оплату и сплитование.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']
        address_id = serializer.validated_data['address_id']
        card_id = serializer.validated_data.get('card_id')
        comment = serializer.validated_data.get('comment', '')

        if not card_id:
            return Response({"error": "Необходимо выбрать карту для оплаты."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Создаем заказ в рамках одной транзакции
            with transaction.atomic():
                order = order_services.create_order_with_calculations(request.user, items_data, address_id, comment)
                card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
                payment_service = PayLinkService()
                payment_service.charge_and_split_payment(order, card)

            full_serializer = OrderSerializer(order)
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.detail[0] if isinstance(e.detail, list) else str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            return Response({"error": f"Ошибка платежной системы: {e.detail}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при создании и оплате заказа: {traceback.format_exc()}")
            return Response({"error": "Произошла внутренняя ошибка на сервере."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

