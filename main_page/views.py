from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Card, Carousel
from .serializers import CardSerializer, CarouselSerializer

class CarouselListView(APIView):
    # List all carousels

    def get(self, request):
        carousel = Carousel.objects.all()
        serializer = CarouselSerializer(carousel, many=True)
        return Response(serializer.data)

class CardListView(APIView):
    # List all cards

    def get(self, request):
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)