# reviews/signals.py (НОВЫЙ ФАЙЛ)
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review

@receiver([post_save, post_delete], sender=Review)
def update_restaurant_rating(sender, instance, **kwargs):
    """
    Сигнал, который автоматически обновляет средний рейтинг ресторана
    при создании, обновлении или удалении отзыва.
    """
    restaurant = instance.order.restaurant
    
    # Получаем все отзывы для данного ресторана
    reviews = Review.objects.filter(order__restaurant=restaurant)
    
    # Вычисляем новый средний рейтинг и количество отзывов
    new_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    review_count = reviews.count()
    
    # Обновляем поля в модели Restaurant
    restaurant.average_rating = new_rating
    restaurant.review_count = review_count
    restaurant.save(update_fields=['average_rating', 'review_count'])