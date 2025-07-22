from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

# Импорты вашего проекта
from .models import Order
from .serializers import OrderSerializer, OrderDetailSerializer, CreateOrderSerializer
from .permissions import IsClientOwnerOfOrder
from .services import calculate_delivery_cost # Сервис для расчета доставки
from payments.services import PayLinkService  # Сервис для оплаты
from core.models import Address
from menu.models import Dish
from promos.models import PromoCode


class OrderListView(generics.ListAPIView):
    """Для клиента: получение списка всех своих заказов."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('restaurant').prefetch_related(
            'items__dish').order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Для клиента: получение деталей одного конкретного заказа."""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]
    queryset = Order.objects.select_related('restaurant').prefetch_related('items__dish').all()


class CreateOrderAndPayView(APIView):
    """
    Принимает данные заказа, создает его в базе данных со всеми расчетами
    и сразу возвращает ссылку на оплату через PayLink.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic # Гарантирует, что если что-то пойдет не так, заказ не создастся
    def post(self, request, *args, **kwargs):
        # 1. Валидируем входящие данные (корзина, адрес, промокод)
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # 2. Создаем заказ в базе данных, вызывая метод .save() из сериализатора.
        # Внутри этого метода у вас происходит вся основная бизнес-логика.
        order = serializer.save()

        # 3. Проверяем, что заказ был создан и у него есть итоговая цена
        if not order or not getattr(order, 'total_price', None):
            return Response(
                {"error": "Не удалось создать заказ или рассчитать итоговую стоимость."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 4. Вызываем сервис PayLink для создания ссылки на оплату
        try:
            paylink_service = PayLinkService()
            payment_url = paylink_service.create_payment(
                amount=float(order.total_price),
                order_id=str(order.id),
                description=f"Оплата заказа №{order.id} в JetFood",
                user_id=request.user.id # Передаем ID пользователя для привязки карт
            )

            if not payment_url:
                raise Exception("Сервис оплаты не вернул URL.")
            
            # 5. Возвращаем ссылку на оплату во Flutter-приложение
            return Response({"payment_url": payment_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Если на этапе создания платежа произошла ошибка, откатываем создание заказа
            transaction.set_rollback(True)
            return Response(
                {"error": f"Ошибка при создании платежа: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalculateOrderCostView(APIView):
    """
    Рассчитывает итоговую стоимость заказа (включая доставку и скидки)
    БЕЗ его создания в базе данных.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        # 1. Расчет стоимости товаров
        items_data = validated_data['items']
        items_total_price = Decimal(0)
        for item_data in items_data:
            dish = Dish.objects.get(id=item_data['dish_id'])
            items_total_price += dish.price * item_data['quantity']

        # 2. Расчет доставки
        address = get_object_or_404(Address, id=validated_data['address_id'])
        restaurant = Dish.objects.get(id=items_data[0]['dish_id']).restaurant
        delivery_fee = calculate_delivery_cost(restaurant, address)

        # 3. Расчет скидки по промокоду
        discount = Decimal(0)
        promo_code_str = validated_data.get('promo_code')
        if promo_code_str:
            try:
                promo = PromoCode.objects.get(code__iexact=promo_code_str)
                if promo.is_valid():
                    discount = promo.calculate_discount(items_total_price)
            except PromoCode.DoesNotExist:
                pass
        
        # 4. Расчет итоговой суммы
        total_price = items_total_price + delivery_fee - discount

        return Response({
            'items_total_price': f"{items_total_price:.2f}",
            'delivery_fee': f"{delivery_fee:.2f}",
            'discount': f"{discount:.2f}",
            'total_price': f"{total_price:.2f}"
        })


class CancelOrderView(APIView):
    """Для клиента: отмена своего заказа."""
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOfOrder]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        self.check_object_permissions(request, order)
        
        if order.status not in [Order.Status.PENDING, Order.Status.ACCEPTED]:
            return Response({'error': 'Этот заказ уже нельзя отменить.'}, status=status.HTTP_400_BAD_REQUEST)
            
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status'])
        return Response({'status': 'Заказ успешно отменен'}, status=status.HTTP_200_OK)