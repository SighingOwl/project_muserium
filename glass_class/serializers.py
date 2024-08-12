from rest_framework import serializers
from .models import GlassClass, Reservation

class ClassSerializer(serializers.ModelSerializer):
	class Meta:
		model = GlassClass
		fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Reservation
		fields = '__all__'