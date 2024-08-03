from rest_framework import serializers
from .models import Card, Carousel

class CardSerializer(serializers.ModelSerializer):
	class Meta:
		model = Card
		fields = '__all__'

class CarouselSerializer(serializers.ModelSerializer):
	class Meta:
		model = Carousel
		fields = '__all__'