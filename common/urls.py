from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('reviews/create/class/<int:glass_class_id>', views.create_class_review, name='create_class_review'),
    path('reviews/update/class/<int:review_id>', views.update_class_review, name='update_class_review'),
    path('reviews/delete/class%review/<int:review_id>', views.delete_class_review, name='delete_class_review'),
    # Temporary URL for dev server
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
