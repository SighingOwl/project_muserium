from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ['id', 'title', 'short_description', 'price', 'image_url', 'image_alt', 'likes', 'reviews', 'total_rating', 'average_rating', 'questions', 'created_at']

class ProductDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = '__all__'
