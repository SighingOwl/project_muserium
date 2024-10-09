from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Card, Carousel
from .serializers import CardSerializer, CarouselSerializer

class CarouselListViewSets(ModelViewSet):
    permission_classes = (AllowAny,)

    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer

    @action(detail=False, methods=['get'])
    def get_carousel(self, request):
        '''
        Get Main Page Carousel Images
        '''

        serializer = CarouselSerializer(self.queryset, many=True)
        return Response(serializer.data)

class CardListViewSets(ModelViewSet):
    permission_classes = (AllowAny,)

    queryset = Card.objects.all()
    serializer_class = CardSerializer

    @action(detail=False, methods=['get'])
    def get_card(self, request):
        '''
        Get Main Page Cards
        '''

        serializer = CardSerializer(self.queryset, many=True)
        return Response(serializer.data)