from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="JetFood API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/promos/', include('promos.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menus/', include('menu.urls')),
    path("api/orders/", include("orders.urls")),
    path('api/courier/', include('courier.urls')),
    path('api/', include('reviews.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# 👇 Эта строка ОБЯЗАТЕЛЬНА для отдачи медиафайлов (картинок)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
