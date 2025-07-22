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
import random
from .models import PhoneOTP, User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsOwner
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
    API для управления адресами (получение списка, создание, обновление, удаление).
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Возвращает только адреса, принадлежащие текущему пользователю."""
        return Address.objects.filter(user=self.request.user).order_by('-id')

    # 👇 ВОТ ГЛАВНОЕ ИСПРАВЛЕНИЕ, КОТОРОЕ РЕШАЕТ ОШИБКУ 500
    def perform_create(self, serializer):
        """Автоматически привязывает новый адрес к текущему пользователю."""
        serializer.save(user=self.request.user)


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
class SendOTPView(APIView):
    """
    View для запроса и отправки OTP кода на номер телефона.
    """
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')

        if not phone_number:
            return Response({"error": "Номер телефона обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        # Генерируем 4-значный код
        otp_code = str(random.randint(1000, 9999))
        
        # Сохраняем или обновляем код для данного номера
        PhoneOTP.objects.update_or_create(
            phone=phone_number,
            defaults={'otp': otp_code}
        )

        # !!! ВАЖНО: Здесь должна быть интеграция с SMS-сервисом (например, Twilio)
        # для отправки кода на реальный телефон.
        # Для тестирования мы просто выводим код в консоль.
        print(f"--- OTP для номера {phone_number}: {otp_code} ---")

        return Response({"success": "Код успешно отправлен"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    View для проверки OTP кода и входа/регистрации пользователя.
    """
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        otp_code = request.data.get('otp')

        if not phone_number or not otp_code:
            return Response({"error": "Номер телефона и OTP код обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_entry = PhoneOTP.objects.get(phone=phone_number)
        except PhoneOTP.DoesNotExist:
            return Response({"error": "Пожалуйста, сначала запросите код"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_entry.is_expired():
            return Response({"error": "Срок действия кода истек"}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_entry.otp != otp_code:
            return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        # Код верный. Находим или создаем пользователя
        user, created = User.objects.get_or_create(phone=phone_number)

        if created:
            # Можно задать поля по умолчанию для нового пользователя, если нужно
            # user.name = "Новый пользователь"
            user.save()

        # Генерируем JWT токены для пользователя
        refresh = RefreshToken.for_user(user)
        
        # Удаляем использованный OTP
        otp_entry.delete()

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data # Возвращаем данные пользователя
        }, status=status.HTTP_200_OK)
