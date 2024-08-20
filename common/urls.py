from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ClassDetailInfoViewSets

app_name = 'common'

router = DefaultRouter()
router.register(r'detail-info', ClassDetailInfoViewSets, basename='detail_info')


urlpatterns = [
    path('', include(router.urls)),

    # Backend 코드를 rest_framwork로 구현 후 url 수정 예정
    # CSRF Token
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),

    # Reviews
    path('reviews/create/class/', views.create_class_review, name='create_class_review'),
    path('reviews/read/class/', views.read_class_review, name='read_class_review'),
    path('reviews/update/class/', views.update_class_review, name='update_class_review'),
    path('reviews/delete/class/', views.delete_class_review, name='delete_class_review'),

    # questions
    path('question/create/class/', views.create_class_question, name='create_class_question'),
    path('question/read/class/', views.read_class_question, name='read_class_question'),
    path('question/get-question-content/class/', views.get_question_content, name='get_question_content'),
    path('question/update/class/', views.update_class_question, name='update_class_question'),
    path('question/delete/class/', views.delete_class_question, name='delete_class_question'),
    path('question/increase-view-count/', views.increase_question_view_count, name='increase_question_view_count'),
    
    # answers
    path('answer/create/class/', views.create_class_answer, name='create_class_answer'),
    path('answer/update/class/', views.update_class_answer, name='update_class_answer'),
    path('answer/delete/class/', views.delete_class_answer, name='delete_class_answer'),
]
