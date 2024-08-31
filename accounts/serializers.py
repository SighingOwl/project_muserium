
from rest_framework import serializers
from .models import User

class UserInfoSerializer(serializers.Serializer):
    id = serializers.CharField()
    nickname = serializers.CharField()
    email = serializers.CharField()
    mobile = serializers.CharField()
    mobile_e164 = serializers.CharField()
    name = serializers.CharField()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'name', 'mobile',]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],
            mobile=validated_data['mobile'],

        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

    
