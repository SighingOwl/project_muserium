
from rest_framework import serializers

class UserInfoSerializer(serializers.Serializer):
    id = serializers.CharField()
    nickname = serializers.CharField()
    email = serializers.CharField()
    mobile = serializers.CharField()
    mobile_e164 = serializers.CharField()
    name = serializers.CharField()
