from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterAPIView, LoginAPIView, NaverLoginAPIView, NaverCallbackAPIView, NaverUserDataAPIViewSets, LoginToDjangoAPIViewSets, NaverToDjangoLoginView, LogoutAPIView, CheckEmailAPIView

app_name = 'accounts'

routers = DefaultRouter()
routers.register(r'naver-userdata', NaverUserDataAPIViewSets, basename='naver-userdata')
routers.register(r'login-to-django', LoginToDjangoAPIViewSets, basename='login-to-django')

urlpatterns = [
    path('', include(routers.urls)),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/check-email/', CheckEmailAPIView.as_view(), name='check-email'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='naver-logout'),
    path('naver/login/', NaverLoginAPIView.as_view(), name='naver-login'),
    path('naver/callback/', NaverCallbackAPIView.as_view(), name='naver-callback'),
    path('naver/login/success/', NaverToDjangoLoginView.as_view(), name='naver-login-success'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
]
