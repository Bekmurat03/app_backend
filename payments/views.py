from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import traceback

from .models import PaymentCard, TokenizationAttempt
from .serializers import PaymentCardSerializer
from .permissions import IsCardOwner
from .services import PayLinkService

class CreateCardTokenizationView(APIView):
    """Создает данные для привязки карты (URL и ID операции)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        service = PayLinkService()
        try:
            tokenization_data = service.create_card_tokenization_data(request.user)
            return Response(tokenization_data, status=status.HTTP_200_OK)
        except Exception as e:
            error_traceback = traceback.format_exc()
            print("--- ПОЙМАНА ОШИБКА В CreateCardTokenizationView ---")
            print(error_traceback)
            print("--- КОНЕЦ ОШИБКИ ---")
            return Response(
                {"error": f"Произошла внутренняя ошибка сервера: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CheckTokenizationStatusView(APIView):
    """Проверяет статус операции токенизации и сохраняет карту."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, attempt_id):
        try:
            attempt = TokenizationAttempt.objects.get(id=attempt_id, user=request.user)
            return Response({"status": attempt.status})
        except TokenizationAttempt.DoesNotExist:
            return Response({"error": "Попытка не найдена"}, status=status.HTTP_404_NOT_FOUND)


class PaymentCardViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    API для управления платежными картами пользователя.
    Разрешены действия: просмотр списка, просмотр одной, УДАЛЕНИЕ.
    """
    serializer_class = PaymentCardSerializer
    permission_classes = [permissions.IsAuthenticated, IsCardOwner]

    def get_queryset(self):
        return PaymentCard.objects.filter(user=self.request.user)
        
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        card = self.get_object()
        card.set_as_primary()
        return Response({'status': 'Карта установлена как основная'})