from django.db import models
from django.utils import timezone

class PromoBanner(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='promos/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Например: 10.0 = 10%")
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Максимальное количество использований")
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def apply(self):
        self.used_count += 1
        self.save()

    def __str__(self):
        return self.code