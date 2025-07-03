# courier/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from orders.models import Order
from orders.serializers import OrderSerializer
from .models import CourierProfile
from .serializers import CourierProfileSerializer, OrderTrackingSerializer
from rest_framework import generics

class DocumentUploadView(APIView):
    """
    Для курьера: загрузка документов для верификации.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Проверяем, что это курьер
        if request.user.role != 'courier':
            return Response(
                {"error": "Только курьеры могут загружать документы."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Находим или создаем профиль для текущего пользователя
        profile, created = CourierProfile.objects.get_or_create(user=request.user)

        # Передаем данные из запроса в сериализатор
        serializer = CourierProfileSerializer(instance=profile, data=request.data)

        if serializer.is_valid():
            # Если данные валидны, меняем статус на "На проверке" и сохраняем
            serializer.save(verification_status='on_review')
            return Response({"success": "Документы успешно загружены и отправлены на проверку."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CurrentOrderView(generics.RetrieveAPIView):
    """
    Возвращает текущий активный заказ курьера 
    (тот, который он взял и еще не доставил).
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Находим активный заказ (статус 'в пути') для текущего курьера
        order = Order.objects.filter(courier=self.request.user, status='on_the_way').first()
        if not order:
            # Если активного заказа нет, можно вернуть ошибку 404 или пустой ответ.
            # Для простоты вернем ошибку, которую приложение сможет обработать.
            raise generics.NotFound("Активный заказ не найден.")
        return order
class AvailableOrdersView(generics.ListAPIView):
    """
    Для курьера: показывает список заказов, которые готовы к выдаче
    и еще не назначены на другого курьера.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(status='ready_for_pickup', courier__isnull=True).order_by('-created_at')

class CourierAcceptOrderView(APIView):
    """
    Для курьера: позволяет "взять" заказ.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if request.user.role != 'courier':
            return Response({"error": "Только курьеры могут принимать заказы."}, status=status.HTTP_403_FORBIDDEN)
            
        order = get_object_or_404(Order, id=order_id)

        if order.status != 'ready_for_pickup' or order.courier is not None:
            return Response({"error": "Этот заказ уже недоступен."}, status=status.HTTP_400_BAD_REQUEST)
        
        order.courier = request.user
        order.status = 'on_the_way'
        order.save()
        
        # TODO: Отправить пуш клиенту, что курьер выехал
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
class OrderPickedUpView(APIView):
    """ Курьер отмечает, что забрал заказ из ресторана. """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, courier=request.user)
        # Это действие возможно, только если заказ в пути (on_the_way)
        # В реальной жизни тут может быть проверка кода у ресторана
        if order.status == 'on_the_way':
            # Здесь можно добавить доп. статус, например, 'picked_up',
            # но для простоты пока оставим 'on_the_way'.
            # TODO: Отправить PUSH клиенту, что заказ едет.
            return Response({"success": "Статус заказа обновлен."}, status=status.HTTP_200_OK)
        return Response({"error": "Неверный статус заказа."}, status=status.HTTP_400_BAD_REQUEST)


class OrderDeliveredView(APIView):
    """ Курьер отмечает, что доставил заказ клиенту. """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, courier=request.user)
        if order.status == 'on_the_way':
            order.status = 'delivered'
            order.save()
            # TODO: Отправить PUSH клиенту и ресторану, что заказ завершен.
            return Response({"success": "Заказ успешно доставлен."}, status=status.HTTP_200_OK)
        return Response({"error": "Неверный статус заказа."}, status=status.HTTP_400_BAD_REQUEST)
class UpdateCourierLocationView(APIView):
    """
    Для курьера: обновить свое текущее местоположение.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'courier':
            return Response({'error': 'Только курьеры могут обновлять локацию'}, status=status.HTTP_403_FORBIDDEN)
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is not None and longitude is not None:
            user.latitude = latitude
            user.longitude = longitude
            user.save()
            return Response({'status': 'Местоположение обновлено'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Не предоставлены координаты'}, status=status.HTTP_400_BAD_REQUEST)


class OrderTrackingView(APIView):
    """
    Для клиента: получить данные для отслеживания заказа.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            # Клиент может отслеживать только свой заказ
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderTrackingSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)