from rest_framework import generics, status 
from .serializers import ChangePasswordSerializer, PhoneTokenObtainPairSerializer, RegisterSerializer, UserDetailSerializer, UserUpdateSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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