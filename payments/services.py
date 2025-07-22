import requests
from django.conf import settings

class PayLinkService:
    """
    Сервис для взаимодействия с API PayLink.kz.
    """
    def __init__(self):
        # Берем ключи из настроек вашего проекта (settings.py или .env)
        self.api_key = getattr(settings, 'PAYLINK_API_KEY', None)
        self.api_url = "https://api.paylink.kz/v1/payments"
        if not self.api_key:
            raise ValueError("Ключ PAYLINK_API_KEY не настроен в настройках Django.")

    def create_payment(self, amount: float, order_id: str, description: str, user_id: int):
        """
        Создает платеж и возвращает URL для оплаты.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "amount": amount,
            "orderId": order_id,
            "description": description,
            "userId": str(user_id), # Передаем ID пользователя для привязки карт
            "paymentSystems": {
                "card": {
                    "saveCard": True # Разрешаем сохранять карту
                },
                "applePay": {
                    "enabled": True
                },
                "googlePay": {
                    "enabled": True
                }
            },
            # URL'ы, на которые PayLink вернет пользователя после оплаты
            # ЗАМЕНИТЕ your-app-domain.com на ваш реальный домен или адрес приложения
            "successUrl": "jetfood://payment/success",
            "failureUrl": "jetfood://payment/failure",
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status() # Вызовет ошибку, если статус не 2xx
            data = response.json()
            return data.get("url") # Возвращаем саму ссылку на оплату
        except requests.exceptions.RequestException as e:
            # Логируем ошибку и пробрасываем ее дальше
            print(f"Ошибка при обращении к PayLink API: {e}")
            raise