# core/serializers.py (ПОЛНЫЙ КОД)
import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from courier.serializers import CourierProfileSerializer
from .models import User, Address

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о пользователе (включая профиль курьера)."""
    courier_profile = CourierProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone', 'role', 'is_push_enabled', 'courier_profile')

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True, label="Имя")
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'password']
        extra_kwargs = { 'password': {'write_only': True}, 'phone': {'required': True} }

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        username = str(uuid.uuid4())
        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            phone=validated_data['phone'],
            first_name=validated_data['name'],
        )
        return user

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone'
    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        user = User.objects.select_related('courier_profile').filter(phone=phone).first()
        if user and user.check_password(password):
            if not user.is_active: raise serializers.ValidationError("Аккаунт пользователя деактивирован.")
            token = self.get_token(user)
            user_data = UserSerializer(user).data
            return { 'refresh': str(token), 'access': str(token.access_token), 'user': user_data }
        raise serializers.ValidationError("Неверный телефон или пароль")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value): raise serializers.ValidationError("Старый пароль введен неверно.")
        return value
    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value
    def validate(self, data):
        if data['new_password'] == data['old_password']: raise serializers.ValidationError("Новый пароль должен отличаться от старого.")
        return data
    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password); user.save(); return user

# core/serializers.py
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        # Указываем все поля, включая те, что нужны для создания
        fields = ['id', 'user', 'city', 'street', 'house_number', 'latitude', 'longitude', 'is_primary']
        # Поле user будет только для чтения, оно подставится автоматически
        read_only_fields = ['user']