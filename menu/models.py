# menu/models.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.db import models

class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/")

    class Meta:
        # Сортируем категории по имени для консистентности
        ordering = ['name']
        verbose_name = "Категория меню"
        verbose_name_plural = "Категории меню"

    def __str__(self):
        return self.name

class Dish(models.Model):
    restaurant = models.ForeignKey("restaurants.Restaurant", on_delete=models.CASCADE, related_name="dishes")
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Увеличим max_digits для гибкости
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)
    # Полезное поле для временного отключения блюда
    is_available = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        # Сортируем блюда по имени
        ordering = ['name']
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

    def __str__(self):
        return self.name