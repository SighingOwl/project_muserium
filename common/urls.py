from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import DetailInfoViewSets, LikeViewSets, ReviewViewSets, QuestionViewSets, AnswerViewSets

app_name = 'common'

router = DefaultRouter()
router.register(r'detail-info', DetailInfoViewSets, basename='detail_info')
router.register(r'like', LikeViewSets, basename='like')
router.register(r'reviews', ReviewViewSets, basename='review')
router.register(r'questions', QuestionViewSets, basename='question')
router.register(r'answers', AnswerViewSets, basename='answer')



urlpatterns = [
    path('', include(router.urls)),

    # Backend 코드를 rest_framwork로 구현 후 url 수정 예정
    # CSRF Token
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
