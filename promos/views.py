from rest_framework import generics
from .models import PromoBanner
from .serializers import PromoBannerSerializer, PromoCodeSerializer
from rest_framework import status
from .models import PromoCode
from rest_framework.views import APIView
from rest_framework.response import Response

class PromoBannerListView(generics.ListAPIView):
    queryset = PromoBanner.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = PromoBannerSerializer


class ValidatePromoCodeView(APIView):
    def post(self, request):
        code = request.data.get("code", "").strip()
        try:
            promo = PromoCode.objects.get(code__iexact=code)
            if not promo.is_valid():
                return Response({"error": "Промокод недействителен"}, status=400)

            serializer = PromoCodeSerializer(promo)
            return Response(serializer.data)

        except PromoCode.DoesNotExist:
            return Response({"error": "Промокод не найден"}, status=404)