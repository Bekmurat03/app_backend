# app_backend/apps/core/serializers.py (ФИНАЛЬНАЯ ВЕРСИЯ)
import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from courier.serializers import CourierProfileSerializer
from .models import User, Address

User = get_user_model()

# --- 👇👇👇 ВОТ НЕДОСТАЮЩИЙ СЕРИАЛИЗАТОР 👇👇👇 ---
class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных о пользователе (включая профиль курьера).
    """
    courier_profile = CourierProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone', 'role', 'is_push_enabled', 'courier_profile')


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'required': True},
            'role': {'required': False, 'default': 'client'}
        }

    def create(self, validated_data):
        # Генерируем уникальный username, так как он обязателен в модели Django
        username = str(uuid.uuid4())
        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            phone=validated_data['phone'],
            first_name=validated_data['name'],
            role=validated_data.get('role'),
        )
        return user


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone'

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        user = User.objects.filter(phone=phone).first()

        if user and user.check_password(password):
            token = self.get_token(user)
            # Используем UserSerializer, чтобы получить все нужные данные
            user_data = UserSerializer(user).data
            return {
                'refresh': str(token),
                'access': str(token.access_token),
                'user': user_data
            }
        
        raise serializers.ValidationError("Неверный телефон или пароль")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль введен неверно.")
        return value

    def validate(self, data):
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError("Новый пароль должен отличаться от старого.")
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'user', 'title', 'full_address', 'latitude', 'longitude', 'is_primary')
        read_only_fields = ('user',)