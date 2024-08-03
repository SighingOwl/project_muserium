from django.urls import path
from .views import CardListView, CarouselListView

app_name = 'main_page'

urlpatterns = [
    #path('', views.index, name='index'),
    path('api/cards/', CardListView.as_view(), name='card_list'),
    path('api/carousels/', CarouselListView.as_view(), name='carousel_list'),
]
