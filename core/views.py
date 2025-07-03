from core.models import Address
from rest_framework import generics, status, viewsets, permissions
from .serializers import AddressSerializer, ChangePasswordSerializer, PhoneTokenObtainPairSerializer, RegisterSerializer, UserDetailSerializer, UserUpdateSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class PhoneLoginView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Для получения и обновления данных текущего пользователя.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Возвращает объект текущего пользователя
        return self.request.user
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer
class ChangePasswordView(generics.UpdateAPIView):
    """
    Эндпоинт для смены пароля.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
class AddressViewSet(viewsets.ModelViewSet):
    """
    API для управления адресами текущего пользователя.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated] # Доступ только для авторизованных

    def get_queryset(self):
        """
        Возвращает только адреса текущего пользователя.
        """
        return Address.objects.filter(user=self.request.user).order_by('-is_primary', 'title')

    def perform_create(self, serializer):
        """
        Привязывает создаваемый адрес к текущему пользователю.
        """
        # Если это первый адрес, делаем его основным
        is_first_address = not Address.objects.filter(user=self.request.user).exists()
        serializer.save(user=self.request.user, is_primary=is_first_address)
class TogglePushView(APIView):
    """
    Переключает включение/выключение основных уведомлений.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.notifications_enabled = not user.notifications_enabled
        user.save()
        return Response({
            "notifications_enabled": user.notifications_enabled
        })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_push_notifications(request):
    user = request.user
    user.notifications_enabled = not user.notifications_enabled  # 👈 переключаем
    user.save()
    return Response({"notifications_enabled": user.notifications_enabled})