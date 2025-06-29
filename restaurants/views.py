from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, CreateAPIView
from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantWriteSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from menu.models import Dish
from menu.serializers import DishSerializer
from .models import Restaurant

# 👥 Публичный список ресторанов (одобренных)
class ApprovedRestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.filter(is_approved=True)
    serializer_class = RestaurantSerializer


# 📄 Детали ресторана (по ID) — публично
class RestaurantDetailView(RetrieveAPIView):
    queryset = Restaurant.objects.filter(is_approved=True)
    serializer_class = RestaurantSerializer


# 🔐 Ресторан может получить/обновить только СВОЙ ресторан
class MyRestaurantView(RetrieveUpdateAPIView):
    serializer_class = RestaurantWriteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Restaurant.objects.get(owner=self.request.user)


# 🛠️ Админ может создать ресторан
class RestaurantCreateView(CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def restaurant_menu_view(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    dishes = Dish.objects.filter(restaurant=restaurant)
    serializer = DishSerializer(dishes, many=True)
    return Response(serializer.data)


