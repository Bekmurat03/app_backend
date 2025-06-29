# menu/models.py
from django.db import models

class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/")

    def __str__(self):
        return self.name

class Dish(models.Model):
    restaurant = models.ForeignKey("restaurants.Restaurant", on_delete=models.CASCADE, related_name="dishes")
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)

    def __str__(self):
        return self.name
