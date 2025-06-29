# menu/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GlobalCategoryListView,
    MenuByRestaurantView,
    UniqueCategoriesView,
    RestaurantsByCategoryView,
    DishViewSet,
)

router = DefaultRouter()
router.register(r'dishes', DishViewSet, basename='dish')

urlpatterns = [
    path("categories/", UniqueCategoriesView.as_view(), name="menu-categories"),
    path("global-categories/", GlobalCategoryListView.as_view(), name="global-category-list"),
    path("by-category/<int:category_id>/", RestaurantsByCategoryView.as_view(), name="restaurants-by-category"),
    path("<int:restaurant_id>/", MenuByRestaurantView.as_view(), name="restaurant-menu"),
    path("", include(router.urls)),  # 👈 подключаем router
]
