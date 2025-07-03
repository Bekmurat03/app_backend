# reviews/views.py
from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь может видеть только свои отзывы
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Привязываем отзыв к текущему пользователю
        serializer.save(user=self.request.user)