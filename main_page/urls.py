from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardListViewSets, CarouselListViewSets

app_name = 'main_page'

routers = DefaultRouter()
routers.register(r'cards', CardListViewSets, basename = 'cards')
routers.register(r'carousels', CarouselListViewSets, basename = 'carousels')

urlpatterns = [
    path('', include(routers.urls)),
]
