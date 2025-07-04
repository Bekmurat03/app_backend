# reviews/serializers.py
from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'order', 'rating', 'comment', 'created_at')
        read_only_fields = ('user',) # Пользователь подставится автоматически