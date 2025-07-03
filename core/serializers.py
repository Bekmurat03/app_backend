# core/serializers.py
import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from courier.serializers import CourierProfileSerializer
from .models import User, Address # 👈 ИМПОРТИРУЙТЕ Address
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    # Этот сериализатор остается без изменений
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'required': True},
            'role': {'required': False}
        }

    def create(self, validated_data):
        username = str(uuid.uuid4())[:30]
        return User.objects.create_user(
            username=username,
            password=validated_data['password'],
            phone=validated_data['phone'],
            first_name=validated_data['name'],
            role=validated_data.get('role', 'client'),
        )

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    # И этот сериализатор остается без изменений
    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        user = User.objects.filter(phone=phone).first()
        if user and user.check_password(password):
            token = self.get_token(user)

            # 👇 2. Добавляем информацию о профиле курьера в ответ 👇
            courier_profile_data = None
            if hasattr(user, 'courier_profile'):
                courier_profile_data = CourierProfileSerializer(user.courier_profile).data

            return {
                'refresh': str(token),
                'access': str(token.access_token),
                'user': {
                    'id': user.id,
                    'name': user.first_name, # Используем first_name
                    'phone': user.phone,
                    'role': user.role,
                    'notifications_enabled': user.notifications_enabled,
                    'courier_profile': courier_profile_data # 👈 Новое поле
                }
            }
        raise serializers.ValidationError("Неверный телефон или пароль")

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)


# 👇👇👇 ВОТ ИЗМЕНЕНИЯ 👇👇👇

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Новый сериализатор. Используется ТОЛЬКО для чтения детальной информации о пользователе.
    """
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'phone', 'role', 'courier_profile',
            'notifications_enabled', 'promotions_enabled'
        )

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления данных пользователя.
    Теперь включает настройки уведомлений.
    """
    class Meta:
        model = User
        fields = ('first_name', 'notifications_enabled', 'promotions_enabled')


class ChangePasswordSerializer(serializers.Serializer):
    # Этот сериализатор остается без изменений
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
        # Поле user будет только для чтения, оно будет подставляться автоматически
        read_only_fields = ('user',)