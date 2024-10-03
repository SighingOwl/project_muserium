import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from ..models import Card, Carousel
from ..serializers import CardSerializer, CarouselSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_carousels(db):
    return Carousel.objects.bulk_create([
        Carousel(name='Carousel 1'),
        Carousel(name='Carousel 2'),
        Carousel(name='Carousel 3')
    ])

@pytest.fixture
def create_cards(db):
    return Card.objects.bulk_create([
        Card(name='Card 1'),
        Card(name='Card 2'),
        Card(name='Card 3')
    ])

def test_get_carousel(api_client, create_carousels):
    url = reverse('carousel-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data == CarouselSerializer(create_carousels, many=True).data

def test_get_card(api_client, create_cards):
    url = reverse('card-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data == CardSerializer(create_cards, many=True).data