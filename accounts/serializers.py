
from rest_framework import serializers, status
from accounts.models import User

import re

class UserInfoSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.CharField()
    mobile = serializers.CharField()
    mobile_e164 = serializers.CharField()
    name = serializers.CharField()
    postcode = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    address_detail = serializers.CharField(required=False)
    address_extra = serializers.CharField(required=False)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'mobile', 'name', 'postcode', 'address', 'address_detail', 'address_extra',]

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'name', 'mobile',]

    def create(self, validated_data):
        vaild_status, error_message = self.data_validation(validated_data)
        if not vaild_status:
            raise serializers.ValidationError({'error': error_message}, status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],
            mobile=validated_data['mobile'],

        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def data_validation(self, data):
        # email validation
        if 'email' not in data:
            return False, 'email 필드가 비어있습니다.'
        elif not self.is_valid_email(data['email']):
            return False, 'email 형식이 올바르지 않습니다.'
        elif User.objects.filter(email=data['email']).exists():
            return False, '이미 존재하는 이메일입니다.'
            
        # password validation
        if 'password' not in data:
            return False, 'password 필드가 비어있습니다.'
        elif not self.is_vaild_password(data['password']):
            return False, 'password 형식이 올바르지 않습니다.'
        
        # username validation
        if 'username' not in data:
            return False, '사용자 이름 필드가 비어있습니다.'
        
        # name validation
        if 'name' not in data:
            return False, '사용자 이름 필드가 비어있습니다.'
        
        # mobile validation
        if 'mobile' not in data:
            return False, '휴대폰 번호 필드가 비어있습니다.'
        elif not self.is_vaild_mobile(data['mobile']):
            return False, '휴대폰 번호 형식이 올바르지 않습니다.'
        elif User.objects.filter(mobile=data['mobile']).exists():
            return False, '이미 존재하는 휴대폰 번호입니다.'
        
        return True, None
    
    def is_valid_email(self, email):
        # Check if email is valid
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email)

    def is_vaild_password(self, password):
        # Check if password is valid
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
        return re.match(password_regex, password) is not None

    def is_vaild_mobile(self, mobile):
        # Check if mobile number is valid
        mobile_regex = r'010\d{8}$'
        return re.match(mobile_regex, mobile) is not None
