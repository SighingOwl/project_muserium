from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.naver import views as naver_views
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LoginView, LogoutView
from .models import User
from .serializers import UserInfoSerializer

import requests
import certifi

# main domain(http://127.0.0.1:8000)
main_domain = settings.MAIN_DOMAIN
frontend_domain = 'https://localhost:5173'

class NaverLoginAPIView(APIView):
    # 로그인을 위한 창은 누구든 접속이 가능해야 하기 때문에 permission을 AllowAny로 설정
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        client_id = settings.NAVER_CLIENT_ID
        response_type = "code"

        uri = main_domain + "/accounts/naver/callback"
        state = settings.STATE

        url = "https://nid.naver.com/oauth2.0/authorize"
        
        return redirect(f'{url}?response_type={response_type}&client_id={client_id}&redirect_uri={uri}&state={state}')

class NaverCallbackAPIView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        try:
            # Naver Login Parameters
            grant_type = 'authorization_code'
            client_id = settings.NAVER_CLIENT_ID
            client_secret = settings.NAVER_CLIENT_SECRET
            code = request.GET.get('code')
            state = request.GET.get('state')

            parameters = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"

            # token request
            token_request = requests.get(
                f"https://nid.naver.com/oauth2.0/token?{parameters}"
            )

            token_response_json = token_request.json()
            error = token_response_json.get("error", None)

            if error is not None:
                return redirect(f"{frontend_domain}/social-login-cancel/")

            access_token = token_response_json.get("access_token")
            return redirect(f"{frontend_domain}/proceed-login/?access_token={access_token}&code={code}/")
        
        except Exception as e:
            return JsonResponse({
                "error": e,
            }, status=status.HTTP_404_NOT_FOUND)

class UserDataAPIViewSets(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
            '''
            User info get request
            '''

            access_token = request.query_params.get("naver_token", None)
            if access_token is None:
                return JsonResponse({"error": "Access Token is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_info_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}",},
                verify=certifi.where()
            )
            
            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return JsonResponse({"error": "failed to get user information."}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_request.json().get("response")
            serializer = UserInfoSerializer(data=user_info)
            if serializer.is_valid():
                email = serializer.data["email"]
                phone_number = serializer.data["mobile"]
                name = serializer.data["name"]
                nickname = serializer.data["nickname"] if "nickname" in serializer.data else None    
            else:
                return JsonResponse({
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)      

            '''
            #User information check
            '''
            # User의 email 을 받아오지 못한 경우
            if email is None:
                return JsonResponse({
                    "error": "Can't Get Email Information from Naver"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # User의 phone_number를 받아오지 못한 경우
            if phone_number is None:
                return JsonResponse({
                    "error": "Can't Get Phone Number Information from Naver"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # User의 name을 받아오지 못한 경우
            if name is None:
                return JsonResponse({
                    "error": "Can't Get Name Information from Naver"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "email": email,
                "phone_number": phone_number,
                "name": name,
                "nickname": nickname
            }, status=status.HTTP_200_OK)

class LoginToDjangoAPIViewSets(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def login(self, request, *args, **kwargs):
            '''
            User info get request
            '''
            # access_token, code는 naver에서 받은 정보
                # django 서버에서 사용자 인증에 사용되는 jwt token과 다른 토큰
            access_token = request.data.get("access_token", None)
            code = request.data.get("code", None)

            if access_token is None:
                return JsonResponse({"error": "Access Token is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_info_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            
            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return JsonResponse({"error": "failed to get user information."}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_request.json().get("response")
            serializer = UserInfoSerializer(data=user_info)
            if serializer.is_valid():
                email = serializer.data["email"]
            else:
                return JsonResponse({
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)      

            '''
            #User information check
            '''
            # User의 email 을 받아오지 못한 경우
            if email is None:
                return JsonResponse({
                    "error": "Can't Get Email Information from Naver"
                }, status=status.HTTP_400_BAD_REQUEST)

            '''
            Check Requested User Existing
            '''

            try:
                user = User.objects.get(email=email)
                data = {'access_token': access_token, 'code': code}
                
                # accept의 token
                    # JSON 형태의 ({"key"}:"token value")
                    # key는 authtoken_token에 저장
                
                accept = requests.post(
                    f"{main_domain}/accounts/naver/login/success/",
                    data=data,
                    # https 연결을 사용하고 있어 로컬 개발 환경에서만 verify=False를 사용
                    verify=False
                )

                # token 오류 처리
                if accept.status_code != 200:
                    return JsonResponse({"error": "Failed to Signin."}, status=accept.status_code)
                
                refresh = RefreshToken.for_user(user)
                jwt_token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                
                return Response(jwt_token, status=status.HTTP_200_OK)

            # User가 없을 때 회원가입 진행
            except User.DoesNotExist:

                data = {'access_token': access_token, 'code': code}
                accept = requests.post(
                    f"{main_domain}/accounts/naver/login/success/",
                    data=data,
                    # https 연결을 사용하고 있어 로컬 개발 환경에서만 verify=False를 사용
                    verify=False
                )
                return Response(accept.json(), status=status.HTTP_200_OK)

class NaverToDjangoLoginView(SocialLoginView):
    adapter_class = naver_views.NaverOAuth2Adapter
    client_class = OAuth2Client

class NaverLogoutAPIView(LogoutView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        '''
        # Revoke Token
        naver_token = request.data.get('naver_token', None)
        if naver_token is None:
            return JsonResponse({"error": "Naver Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        token_revoke_url = "https://nid.naver.com/oauth2.0/token"
        params = {
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "grant_type": "delete",
            "access_token": naver_token,
            "service_provider": "NAVER"
        }
        reponse = requests.post(token_revoke_url, params=params)
        if reponse.status_code != 200:
            return JsonResponse({"error": "Failed to logout."}, status=reponse.status_code)
        '''
        # django logout
        return super().post(request, *args, **kwargs)