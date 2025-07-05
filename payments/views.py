from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import base64
from django.conf import settings
from .models import PaymentCard
from .serializers import PaymentCardSerializer


class CreateCardTokenizationView(APIView):
    """
    Возвращает redirect_url для привязки карты (Hosted Payment Page)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        credentials = f"{settings.PAYLINK_API_KEY}:{settings.PAYLINK_API_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "X-API-Version": "2"
        }

        payload = {
            "checkout": {
                "transaction_type": "tokenization",
                "order": {
                    "amount": 0,
                    "currency": "KZT",
                    "description": "Привязка карты в JetFood"
                },
                "customer": {
                    "user_id": str(user.id),
                    "email": user.email or f"user{user.id}@jetfood.kz",
                    "phone": user.phone
                },
                "settings": {
                    "success_url": "jetfood://card/success",
                    "failure_url": "jetfood://card/failure"
                }
            }
        }

        try:
            response = requests.post("https://checkout.paylink.kz/ctp/api/checkouts", json=payload, headers=headers)
            response_data = response.json()
            if response.status_code == 201:
                return Response({"tokenization_url": response_data['checkout']['redirect_url']})
            else:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCardViewSet(viewsets.ModelViewSet):
    """
    Сохраняем карту по токену без проверки на стороне PayLink.
    Это упрощённый вариант для тестового окружения.
    """
    serializer_class = PaymentCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentCard.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        token = request.data.get('token')
        name = request.data.get('name', 'Моя карта')  # ✅ Название карты по умолчанию

        if not token:
            return Response({"error": "token обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        if PaymentCard.objects.filter(card_token=token).exists():
            return Response({"detail": "Карта уже сохранена"}, status=status.HTTP_200_OK)

        try:
            PaymentCard.objects.create(
                user=request.user,
                name=name,  # ✅ добавляем название
                card_token=token,
                last_four=token[-4:],
                expiry_month="12",
                expiry_year="2030",
                card_type="PayLink Card"
            )

            return Response({"success": "Карта успешно сохранена"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("❌ Ошибка при сохранении карты:", str(e))
            return Response(
                {"error": "Не удалось сохранить карту", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
