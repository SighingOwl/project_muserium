from rest_framework import serializers
from .models import GlassClass, Reservation

class ClassSerializer(serializers.ModelSerializer):
	class Meta:
		model = GlassClass
		fields = ['id', 'title', 'teacher', 'category', 'short_description', 'price', 'image_url', 'image_alt', 'likes', 'reviews', 'total_rating', 'average_rating', 'questions', 'created_at']

class ClassDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = GlassClass
		fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Reservation
		fields = '__all__'