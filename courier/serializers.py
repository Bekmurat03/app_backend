# courier/serializers.py
from rest_framework import serializers
from .models import CourierProfile
from orders.models import Order
from core.models import User

class CourierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        # Указываем поля, которые приложение будет отправлять
        fields = ['id_card_photo', 'driver_license_photo','verification_status']
# Этот сериализатор будет отдавать ТОЛЬКО публичную информацию о курьере
class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'phone', 'latitude', 'longitude')


# Этот сериализатор будет готовить все данные для экрана отслеживания
class OrderTrackingSerializer(serializers.ModelSerializer):
    courier = CourierSerializer(read_only=True)
    # Достаем широту и долготу из связанной модели ресторана
    restaurant_lat = serializers.FloatField(source='restaurant.latitude', read_only=True)
    restaurant_lon = serializers.FloatField(source='restaurant.longitude', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'status', 'courier', 'restaurant_lat', 'restaurant_lon', 'preparation_time','created_at',
                  'estimated_delivery_time','delivery_lat','delivery_lon'
                  )

# Этот сериализатор у вас уже есть, просто убедитесь, что он на месте
class CourierOrderSerializer(serializers.ModelSerializer):
     class Meta:
        model = Order
        fields = '__all__'