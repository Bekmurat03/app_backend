from decimal import Decimal
import math
import logging
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError

from .models import Order, OrderItem
from core.models import Address, User
from restaurants.models import Restaurant
from menu.models import Dish

logger = logging.getLogger(__name__)


def get_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 0
    R = 6371;
    rad = lambda x: float(x) * math.pi / 180;
    dLat = rad(Decimal(lat2) - Decimal(lat1));
    dLon = rad(Decimal(lon2) - Decimal(lon1))
    a = (math.sin(dLat / 2) ** 2) + math.cos(rad(Decimal(lat1))) * math.cos(rad(Decimal(lat2))) * (
                math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    return R * c


def calculate_delivery_fee(restaurant: Restaurant, address: Address) -> Decimal:
    """
    Рассчитывает стоимость доставки на основе тарифов ресторана и расстояния.
    """
    # 1. Проверяем, что все координаты на месте
    if not all([restaurant.latitude, restaurant.longitude, address.latitude, address.longitude]):
        # Если координат нет, возвращаем базовую стоимость из первого тарифа или стандартную
        first_tariff = restaurant.tariffs.first()
        return first_tariff.base_fee if first_tariff else Decimal('500.00')

    # 2. Находим подходящий тариф на текущее время
    now = timezone.now().time()
    active_tariff = None
    for tariff in restaurant.tariffs.all():
        # Логика для тарифов, которые пересекают полночь (например, 22:00 - 06:00)
        if tariff.start_time > tariff.end_time:
            if now >= tariff.start_time or now <= tariff.end_time:
                active_tariff = tariff
                break
        # Логика для обычных дневных тарифов
        else:
            if tariff.start_time <= now < tariff.end_time:
                active_tariff = tariff
                break
    
    # Если тариф не найден, используем первый доступный или стандартную цену
    if not active_tariff:
        active_tariff = restaurant.tariffs.first()
        if not active_tariff:
            return Decimal('500.00')

    # 3. Рассчитываем расстояние в километрах
    restaurant_coords = (restaurant.latitude, restaurant.longitude)
    customer_coords = (address.latitude, address.longitude)
    distance_km = geodesic(restaurant_coords, customer_coords).kilometers
    
    # 4. Считаем итоговую стоимость доставки
    calculated_cost = active_tariff.base_fee + (Decimal(distance_km) * active_tariff.fee_per_km)
    
    # Округляем до ближайших 50 KZT, как в вашей логике
    return Decimal(round(calculated_cost / 50) * 50)


def calculate_order_totals(items_data: list, address: Address) -> dict:
    if not items_data: raise ValidationError("Корзина пуста.")

    # 👇 ИСПРАВЛЕНО: Правильно извлекаем ID из списка словарей
    dish_ids = [item.get('menu') for item in items_data]

    dishes = Dish.objects.filter(id__in=dish_ids).select_related('restaurant')
    if not dishes.exists() or len(dish_ids) != dishes.count():
        raise ValidationError("Одно или несколько блюд в заказе не найдены.")

    restaurant = dishes.first().restaurant

    items_total_price = sum(
        dish.price * next(item['quantity'] for item in items_data if item.get('menu') == dish.id) for dish in dishes)
    delivery_fee = calculate_delivery_fee(restaurant, address)
    service_fee = max(Decimal(settings.MIN_CLIENT_SERVICE_FEE),
                      min(items_total_price * (Decimal(settings.CLIENT_SERVICE_FEE_PERCENT) / 100),
                          Decimal(settings.MAX_CLIENT_SERVICE_FEE)))
    total_price = items_total_price + delivery_fee + service_fee

    return {
        "items_total_price": items_total_price,
        "delivery_fee": delivery_fee,
        "service_fee": service_fee,
        "total_price": total_price
    }


@transaction.atomic
def create_order_with_calculations(user: User, items_data: list, address_id: int, comment: str) -> Order:
    try:
        address_obj = Address.objects.get(id=address_id, user=user)
    except Address.DoesNotExist:
        raise ValidationError("Указанный адрес не найден.")

    totals = calculate_order_totals(items_data, address_obj)

    first_dish = Dish.objects.select_related('restaurant').get(id=items_data[0]['menu'])
    restaurant = first_dish.restaurant

    restaurant_commission = totals['items_total_price'] * (Decimal(settings.RESTAURANT_COMMISSION_PERCENT) / 100)

    order = Order.objects.create(
        user=user, restaurant=restaurant, address=address_obj.full_address,
        delivery_lat=address_obj.latitude, delivery_lon=address_obj.longitude,
        comment=comment, payment_method='card_online', **totals,
        platform_fee=restaurant_commission + totals['service_fee'],
        restaurant_payout=totals['items_total_price'] - restaurant_commission,
        courier_payout=totals['delivery_fee'],
    )

    order_items_to_create = [
        OrderItem(order=order, menu_id=item['menu'], quantity=item['quantity'],
                  price_at_time_of_order=Dish.objects.get(id=item['menu']).price)
        for item in items_data
    ]
    OrderItem.objects.bulk_create(order_items_to_create)

    return order
import math
from decimal import Decimal
from django.utils import timezone
from geopy.distance import geodesic # Используем стандартную, надежную библиотеку

# Импорты ваших моделей
from restaurants.models import Restaurant, DeliveryTariff
from core.models import Address


def calculate_delivery_cost(restaurant: Restaurant, address: Address) -> Decimal:
    """
    Рассчитывает стоимость доставки на основе тарифов ресторана и расстояния.
    """
    # 1. Проверяем, что все координаты на месте
    if not all([restaurant.latitude, restaurant.longitude, address.latitude, address.longitude]):
        first_tariff = restaurant.tariffs.first()
        return first_tariff.base_fee if first_tariff else Decimal('500.00')

    # 2. Находим подходящий тариф на текущее время
    now = timezone.now().time()
    active_tariff = None
    # Сортируем, чтобы гарантировать предсказуемый выбор, если есть пересечения
    for tariff in restaurant.tariffs.all().order_by('id'): 
        if tariff.start_time > tariff.end_time: # Для тарифов, пересекающих полночь
            if now >= tariff.start_time or now <= tariff.end_time:
                active_tariff = tariff
                break
        else: # Для обычных дневных тарифов
            if tariff.start_time <= now < tariff.end_time:
                active_tariff = tariff
                break
    
    # Если активный тариф не найден, берем первый попавшийся
    if not active_tariff:
        active_tariff = restaurant.tariffs.first()
        if not active_tariff:
            return Decimal('500.00') # Запасной вариант, если тарифов нет

    # 3. Рассчитываем расстояние в километрах
    restaurant_coords = (restaurant.latitude, restaurant.longitude)
    customer_coords = (address.latitude, address.longitude)
    distance_km = geodesic(restaurant_coords, customer_coords).kilometers
    
    # 4. Считаем стоимость, проверяя, что поля не пустые (не None)
    base_fee = active_tariff.base_fee or Decimal('0.00')
    fee_per_km = active_tariff.fee_per_km or Decimal('0.00')
    
    calculated_cost = base_fee + (Decimal(distance_km) * fee_per_km)
    
    # Округляем до ближайших 50 KZT
    return Decimal(round(calculated_cost / 50) * 50)