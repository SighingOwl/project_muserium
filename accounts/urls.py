from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import NaverLoginAPIView, NaverCallbackAPIView, UserDataAPIViewSets, LoginToDjangoAPIViewSets, NaverToDjangoLoginView, NaverLogoutAPIView

app_name = 'accounts'

routers = DefaultRouter()
routers.register(r'naver-userdata', UserDataAPIViewSets, basename='naver-userdata')
routers.register(r'login-to-django', LoginToDjangoAPIViewSets, basename='login-to-django')

urlpatterns = [
    path('', include(routers.urls)),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('naver/login/', NaverLoginAPIView.as_view(), name='naver-login'),
    path('naver/callback/', NaverCallbackAPIView.as_view(), name='naver-callback'),
    path('naver/login/success/', NaverToDjangoLoginView.as_view(), name='naver-login-success'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('naver/logout/', NaverLogoutAPIView.as_view(), name='naver-logout'),
]
