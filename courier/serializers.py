# courier/serializers.py (ПОЛНЫЙ КОД)
from rest_framework import serializers
from .models import CourierProfile
from orders.models import Order
from core.models import User
from restaurants.serializers import RestaurantSerializer
from orders.serializers import OrderItemSerializer # Этот импорт теперь безопасен

class CourierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        fields = ['id_card_photo', 'driver_license_photo', 'verification_status', 'is_online']
        read_only_fields = ('verification_status',)

class PublicCourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'phone', 'latitude', 'longitude')

class OrderTrackingSerializer(serializers.ModelSerializer):
    courier = PublicCourierSerializer(read_only=True)
    restaurant_lat = serializers.FloatField(source='restaurant.latitude', read_only=True)
    restaurant_lon = serializers.FloatField(source='restaurant.longitude', read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'status', 'courier', 'restaurant_lat', 'restaurant_lon', 'preparation_time','created_at', 'estimated_delivery_time', 'delivery_lat','delivery_lon')

class CourierOrderSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [ 'id', 'code', 'address', 'comment', 'total_price', 'delivery_fee', 'status', 'created_at', 'restaurant', 'items', 'delivery_lat', 'delivery_lon' ]