# orders/views.py
from rest_framework import generics, permissions, status
from .models import Order
from .serializers import OrderSerializer
from restaurants.models import Restaurant
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class OrderListCreateView(generics.ListCreateAPIView):
    """ Для клиента: просмотр своих заказов и создание нового. """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RestaurantOrdersView(generics.ListAPIView):
    """ Для ресторана: просмотр всех заказов, которые к нему относятся. """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            restaurants = Restaurant.objects.filter(owner=user)
            return Order.objects.filter(restaurant__in=restaurants).distinct().order_by('-created_at')
        except Restaurant.DoesNotExist:
            return Order.objects.none()

# 👇👇👇 ДОБАВЬТЕ/ЗАМЕНИТЕ НА ЭТИ КЛАССЫ 👇👇👇

class AcceptOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant)

        if order.status == 'pending':
            order.status = 'accepted'
            order.save()
            return Response({'status': 'Заказ принят'}, status=status.HTTP_200_OK)
        return Response({'error': 'Этот заказ нельзя принять.'}, status=status.HTTP_400_BAD_REQUEST)

class RejectOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant)

        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'Заказ отклонен'}, status=status.HTTP_200_OK)
        return Response({'error': 'Этот заказ нельзя отклонить.'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant)

        if order.status == 'accepted':
            order.status = 'preparing'
        elif order.status == 'preparing':
            order.status = 'ready_for_pickup'
            # 👇👇👇 ВОТ НАША ЗАГЛУШКА 👇👇👇
            # TODO: В будущем здесь будет логика отправки пуш-уведомлений
            # всем свободным курьерам о том, что появился новый готовый заказ.
            # find_available_couriers_and_notify(order)
            # 👆👆👆 КОНЕЦ ЗАГЛУШКИ 👆👆👆
        else:
            return Response({'error': f'Нельзя изменить статус с "{order.status}"'}, status=status.HTTP_400_BAD_REQUEST)

        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class OrderDetailView(generics.RetrieveAPIView):
    """
    Для клиента: получение деталей одного конкретного заказа.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Клиент может видеть только свои заказы
        return Order.objects.filter(user=self.request.user)