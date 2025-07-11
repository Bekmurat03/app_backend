# courier/views.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)
from payments.services import PayLinkService
from rest_framework import generics, status, views
# 👇 ИСПРАВЛЕНО: Добавляем недостающий импорт 'permissions'
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
import logging
from orders.models import Order
from .models import CourierProfile
from .serializers import CourierProfileSerializer, CourierOrderSerializer, OrderTrackingSerializer
from .permissions import IsCourier, IsOrderCourier
from . import services

# --- Управление профилем курьера ---
logger = logging.getLogger(__name__)

class DocumentUploadView(views.APIView):
    """Для курьера: загрузка/обновление документов для верификации."""
    permission_classes = [IsCourier]

    def post(self, request, *args, **kwargs):
        profile, created = CourierProfile.objects.get_or_create(user=request.user)
        # partial=True позволяет обновлять только переданные поля
        serializer = CourierProfileSerializer(instance=profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(verification_status='on_review')
            return Response({"success": "Документы успешно загружены."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleOnlineStatusView(views.APIView):
    """Для курьера: переключение статуса онлайн/оффлайн."""
    permission_classes = [IsCourier]

    def post(self, request, *args, **kwargs):
        profile, created = CourierProfile.objects.get_or_create(user=request.user)
        profile.is_online = not profile.is_online
        profile.save(update_fields=['is_online'])
        return Response({'is_online': profile.is_online}, status=status.HTTP_200_OK)


class UpdateCourierLocationView(views.APIView):
    """Для курьера: обновить свое текущее местоположение."""
    permission_classes = [IsCourier]
    
    def post(self, request, *args, **kwargs):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if latitude is not None and longitude is not None:
            request.user.latitude = latitude
            request.user.longitude = longitude
            request.user.save(update_fields=['latitude', 'longitude'])
            return Response({'status': 'Местоположение обновлено'}, status=status.HTTP_200_OK)
        return Response({'error': 'Не предоставлены координаты'}, status=status.HTTP_400_BAD_REQUEST)


# --- Работа с заказами ---

class AvailableOrdersView(generics.ListAPIView):
    """Для курьера: список заказов, готовых к выдаче."""
    serializer_class = CourierOrderSerializer
    permission_classes = [IsCourier]

    def get_queryset(self):
        return Order.objects.filter(status='ready_for_pickup', courier__isnull=True).select_related(
            'restaurant'
        ).prefetch_related(
            'items__menu'
        ).order_by('-created_at')


class CourierAcceptOrderView(views.APIView):
    """Для курьера: "взять" заказ."""
    permission_classes = [IsCourier]

    def post(self, request, order_id):
        try:
            order = services.accept_order_for_courier(order_id, request.user)
            serializer = CourierOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentOrderView(generics.RetrieveAPIView):
    """Возвращает текущий активный заказ курьера."""
    serializer_class = CourierOrderSerializer
    permission_classes = [IsCourier]

    def get_object(self):
        order = Order.objects.select_related('restaurant').prefetch_related('items__menu').filter(
            courier=self.request.user, status='on_the_way'
        ).first()
        if not order:
            raise NotFound("Активный заказ не найден.")
        return order


class UpdateDeliveryStatusView(APIView):
    """
    Для курьера: отметить, что забрал заказ или доставил.
    При доставке инициирует списание и сплитование.
    """
    permission_classes = [permissions.IsAuthenticated, IsCourier, IsOrderCourier]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        self.check_object_permissions(request, order)

        action = request.data.get('action')

        if action == 'picked_up' and order.status == 'ready_for_pickup':
            order.status = 'on_the_way'
            order.save(update_fields=['status'])
            return Response({"success": "Статус обновлен: 'В пути'."}, status=status.HTTP_200_OK)

        elif action == 'delivered' and order.status == 'on_the_way':
            try:
                with transaction.atomic():
                    order.status = 'delivered'
                    order.save(update_fields=['status'])
                    
                    if order.authorization_id:
                        payment_service = PayLinkService()
                        payment_service.capture_and_split_payment(order)

                return Response({"success": "Заказ успешно доставлен. Оплата списана."}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Критическая ошибка при завершении заказа {order.id}: {str(e)}")
                return Response({"error": "Не удалось завершить заказ и списать оплату."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"error": f"Неверное действие '{action}' для заказа со статусом '{order.get_status_display()}'."}, status=status.HTTP_400_BAD_REQUEST)


class CourierOrderHistoryView(generics.ListAPIView):
    """Для курьера: возвращает всю историю его заказов."""
    serializer_class = CourierOrderSerializer
    permission_classes = [IsCourier]

    def get_queryset(self):
        return Order.objects.filter(courier=self.request.user).select_related(
            'restaurant'
        ).prefetch_related('items__menu').order_by('-created_at')


class CourierStatsView(views.APIView):
    """Возвращает статистику для текущего курьера."""
    permission_classes = [IsCourier]

    def get(self, request, *args, **kwargs):
        # ... (логика без изменений) ...
        courier = request.user
        today = timezone.now().date()
        today_stats = Order.objects.filter(courier=courier, status='delivered', created_at__date=today).aggregate(
            earnings_today=Sum('delivery_fee'), orders_today=Count('id')
        )
        total_stats = Order.objects.filter(courier=courier, status='delivered').aggregate(
            earnings_total=Sum('delivery_fee'), orders_total=Count('id')
        )
        return Response({
            'earnings_today': today_stats.get('earnings_today') or 0,
            'orders_today': today_stats.get('orders_today') or 0,
            'earnings_total': total_stats.get('earnings_total') or 0,
            'orders_total': total_stats.get('orders_total') or 0,
        })


# --- VIEW ДЛЯ КЛИЕНТА ---

class OrderTrackingView(generics.RetrieveAPIView):
    """Для клиента: получить данные для отслеживания заказа."""
    # Вот здесь была ошибка, теперь `permissions` определен
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderTrackingSerializer
    queryset = Order.objects.select_related('courier', 'restaurant').all()

    def get_object(self):
        order = get_object_or_404(self.get_queryset(), id=self.kwargs['order_id'], user=self.request.user)
        return order