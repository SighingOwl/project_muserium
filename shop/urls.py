from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListViewSets, ProductViewSets

app_name = 'shop'

router = DefaultRouter()
router.register(r'products', ProductListViewSets, basename='products')
router.register(r'detail', ProductViewSets, basename='product_detail')

urlpatterns = [
    path('', include(router.urls)),
]
