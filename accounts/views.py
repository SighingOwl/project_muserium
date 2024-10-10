from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.naver import views as naver_views
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from accounts.models import User
from accounts.serializers import UserInfoSerializer, RegisterSerializer, UserSerializer

import requests
import certifi

main_domain = settings.MAIN_DOMAIN
frontend_domain = 'https://localhost:5173'

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if email is None:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if password is None:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return Response({"error": "Password is incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = TokenObtainPairSerializer().get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        return Response({
            "refresh": refresh_token,
            "access": access_token,
            "user": {
                "email": user.email,
                "name": user.name,
                "mobile": user.mobile,
                "postcode": user.postcode,
                "address": user.address,
                "address_detail": user.address_detail,
                "address_extra": user.address_extra,
            }
        }, status=status.HTTP_200_OK)

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
            return Response({
                "error": e,
            }, status=status.HTTP_404_NOT_FOUND)

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
                return Response({"error": "Access Token is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_info_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            

            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return Response({"error": "failed to get user information."}, status=status.HTTP_400_BAD_REQUEST)
        
            user_info = user_info_request.json().get("response")
            serializer = UserInfoSerializer(data=user_info)
            if serializer.is_valid():
                email = serializer.validated_data.get("email")
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            '''
            #User information check
            '''
            # User의 email 을 받아오지 못한 경우
            if email is None:
                return Response({"error": "네이버에서 이메일 정보를 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)

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
                    return Response({"error": "로그인에 실패했습니다."}, status=accept.status_code)
                
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

class NaverUserDataAPIViewSets(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
            '''
            User info get request
            '''
            access_token = request.query_params.get("naver_token", None)
            if access_token is None:
                return Response({"error": "Naver Token is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_info_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}",},
                verify=certifi.where()
            )
            
            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return Response({"error": "네이버에서 사용자 정보를 가져오는데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_request.json().get("response")
            serializer = UserInfoSerializer(data=user_info)
            if serializer.is_valid():
                email = serializer.validated_data.get("email")
                mobile = serializer.validated_data.get("mobile")
                name = serializer.validated_data.get("name")
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)      

            '''
            #User information check
            '''
            # User의 email 을 받아오지 못한 경우
            if email is None:
                return Response({"error": "네이버에서 이메일 정보를 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # User의 mobile를 받아오지 못한 경우
            if mobile is None:
                return Response({"error": "네이버에서 휴대폰 번호 정보를 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # User의 name을 받아오지 못한 경우
            if name is None:
                return Response({"error": "네이버에서 이름 정보를 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_data = User.objects.get(email=email)
                if user_data.mobile != mobile:
                    user_data.mobile = mobile
                    user_data.save()

                if user_data.name != name:
                    user_data.name = name
                    user_data.save()
                
                user = UserSerializer(user_data)
            except User.DoesNotExist:
                user = {
                    "email": email,
                    "mobile": mobile,
                    "name": name,
                }

            return Response(user.data, status=status.HTTP_200_OK)
    
class LogoutAPIView(LogoutView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        '''
        # Revoke Token
        naver_token = request.data.get('naver_token', None)
        if naver_token is None:
            return Response({"error": "Naver Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
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
            return Resp의onse({"error": "Failed to logout."}, status=reponse.status_code)
        '''
        # django logout
        return super().post(request, *args, **kwargs)


'''
User Data API
RegisterAPIView: 회원가입 API
UpdateUserAPIView: 사용자 정보 변경 API
CheckEmailAPIView: 이메일 중복 확인 API
RestoreEmail: 이메일 찾기 API
ResetPassword: 비밀번호 초기화 API
'''
class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            token = TokenObtainPairSerializer().get_token(serializer.instance)
            refresh_token = str(token)
            access_token = str(token.access_token)

            user = User.objects.get(email=serializer.data['email'])
            
            return Response({
                "refresh": refresh_token,
                "access": access_token,
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "mobile": user.mobile,
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, email = request.query_params.get('email', None))
        
        if request.headers.get('new_password', None) is not None:
            if not user.check_password(request.headers.get('current_password')):
                return Response({"error": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not self.is_valid_password(request.headers.get('new_password')):
                return Response({"error": "비밀번호 형식이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(request.headers.get('new_password'))
        
        if request.data.get('mobile', None) is not None:
            if not self.is_valid_mobile(request.data.get('mobile')):
                return Response({"error": "휴대폰 번호 형식이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            user.mobile = request.data.get('mobile')
        
        if request.data.get('postcode', None) is not None:
            user.postcode = request.data.get('postcode')
            user.address = request.data.get('address')
            user.address_detail = request.data.get('address_detail')
            user.address_extra = request.data.get('address_extra', None)
        
        user.save()
        return Response({"message": "정보가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
    
    # vaildation check
    def is_valid_mobile(self, mobile):
        import re

        mobile_regex = r'^010\d{8}$'
        return re.match(mobile_regex, mobile) is not None
    
    def is_valid_password(self, password):
        import re

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
        return re.match(password_regex, password) is not None

    
class CheckEmailAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)
        if email is None:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            return Response({"exists": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"exists": False}, status=status.HTTP_200_OK)

class RestoreEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        name = request.data.get('name', None)
        mobile = request.data.get('mobile', None)
        if name is None:
            return Response({"error": "사용자 이름 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        if mobile is None:
            return Response({"error": "휴대폰 번호 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(name=name, mobile=mobile)
            return Response({"email": user.email}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
class ResetPassword(APIView):
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        name = request.data.get('name', None)
        if email is None:
            return Response({"error": "이메일 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        if name is None:
            return Response({"error": "사용자 이름 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 추후에 이메일로 전송하는 방식으로 변경 -> amazon ses 사용
            user = User.objects.get(email=email, name=name)
            password = self.generate_password()
            user.set_password(password)
            user.save()
            return Response({"password": password}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
    def generate_password(self):
        import random
        import string

        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))

        return password
    
class IsAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"is_admin": request.user.is_superuser}, status=status.HTTP_200_OK)