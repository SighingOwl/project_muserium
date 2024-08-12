from django.urls import path
from .views import ClassListView, ClassDetailView, ClassReservationView

app_name = 'glass_class'

urlpatterns = [
    #path('', views.index, name='index'),
    path('api/', ClassListView.as_view(), name='class_list'),
    path('api/<str:key>/', ClassDetailView.as_view(), name='class_detail'),
    path('api/<str:key>/reservations/', ClassReservationView.as_view(), name='class_reservation_list'),
]
