from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('reviews/create/class/', views.create_class_review, name='create_class_review'),
    path('reviews/read/class/', views.read_class_review, name='read_class_review'),
    path('reviews/update/class/', views.update_class_review, name='update_class_review'),
    path('reviews/delete/class%review/', views.delete_class_review, name='delete_class_review'),
    # Temporary URL for dev server
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
