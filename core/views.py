# app_backend/apps/core/views.py (ОБНОВЛЕННАЯ ВЕРСИЯ)

from rest_framework import generics, status, viewsets, permissions
from .models import Address, User
from .serializers import (
    AddressSerializer,
    ChangePasswordSerializer,
    PhoneTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # Разрешаем регистрацию всем (неаутентифицированным пользователям)
    permission_classes = [permissions.AllowAny]


class PhoneLoginView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Для получения и обновления данных текущего пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 👇 УЛУЧШЕНИЕ 2: Оптимизируем запрос и здесь.
        # Мы получаем request.user, но чтобы сериализатор отработал
        # без лишних запросов, нам нужно получить объект с .select_related().
        user = User.objects.select_related('courier_profile').get(id=self.request.user.id)
        return user


class ChangePasswordView(generics.UpdateAPIView):
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Запрос уже оптимален, так как работает только с адресами
        return Address.objects.filter(user=self.request.user).order_by('-is_primary', 'title')

    def perform_create(self, serializer):
        # Логика для установки первого адреса как основного - это хороший UX.
        user = self.request.user
        # Проверяем, есть ли у пользователя уже какие-либо адреса.
        is_first_address = not Address.objects.filter(user=user).exists()
        # Если это первый адрес, делаем его основным (is_primary=True).
        serializer.save(user=user, is_primary=is_first_address)


class TogglePushNotificationView(APIView):
    """
    Переключает включение/выключение основных уведомлений.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_push_enabled = not user.is_push_enabled
        user.save(update_fields=['is_push_enabled'])
        return Response({
            "is_push_enabled": user.is_push_enabled
        }, status=status.HTTP_200_OK)