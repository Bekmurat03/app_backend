from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer
from restaurants.models import Restaurant
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class RestaurantOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = Restaurant.objects.get(owner=user, is_approved=True)
        except Restaurant.DoesNotExist:
            return Order.objects.none()

        return Order.objects.filter(
            items__menu__restaurant=restaurant
        ).distinct().order_by('-created_at')

class RestaurantOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Находим ресторан по владельцу (пользователю)
        try:
            restaurant = Restaurant.objects.get(owner=request.user)
        except Restaurant.DoesNotExist:
            return Response([], status=200)  # У пользователя нет ресторана

        # Получаем все заказы, в которых есть блюда из этого ресторана
        orders = Order.objects.filter(items__menu__restaurant=restaurant).distinct().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class MarkOrderReadyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            restaurant = Restaurant.objects.get(owner=request.user)
            order = Order.objects.get(id=order_id)

            # Проверяем, что заказ относится к ресторану пользователя
            if order.items.first().menu.restaurant != restaurant:
                return Response({"error": "Нет доступа к заказу"}, status=403)

            if order.status != "accepted":
                return Response({"error": "Заказ не в статусе 'Принят'"}, status=400)

            order.status = "preparing"
            order.save()
            return Response({"message": "Заказ отмечен как готовится"}, status=200)

        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден"}, status=404)
        except Restaurant.DoesNotExist:
            return Response({"error": "Ресторан не найден"}, status=404)
class OrderDetailView(generics.RetrieveAPIView):
    """
    Для клиента: получение деталей одного конкретного заказа.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Клиент может видеть только свои заказы
        return Order.objects.filter(user=self.request.user)