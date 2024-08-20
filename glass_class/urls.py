from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassListViewSets, ClassViewSets, ClassReservationViewSets

app_name = 'glass_class'

router = DefaultRouter()
router.register(r'classes', ClassListViewSets, basename='class')
router.register(r'detail', ClassViewSets, basename='class_detail')
router.register(r'reservation', ClassReservationViewSets, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]
