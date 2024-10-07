import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from main_page.models import Card, Carousel
from ..serializers import CardSerializer, CarouselSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_carousels(db):
    return Carousel.objects.bulk_create([
        Carousel(title='Carousel 1', image_url='https://example.com/image1.jpg', background_color='#000000', alt='Image 1'),
        Carousel(title='Carousel 2', image_url='https://example.com/image2.jpg', background_color='#000000', alt='Image 2'),
        Carousel(title='Carousel 3', image_url='https://example.com/image3.jpg', background_color='#000000', alt='Image 3'),
        Carousel(title='Carousel 4', image_url='https://example.com/image4.jpg', background_color='#000000', alt='Image 4'),
    ])

@pytest.fixture
def create_cards(db):
    return Card.objects.bulk_create([
        Card(title='Card 1', image_url='https://example.com/image1.jpg', alt='Image 1', url='https://example.com'),
        Card(title='Card 2', image_url='https://example.com/image2.jpg', alt='Image 2', url='https://example.com'),
        Card(title='Card 3', image_url='https://example.com/image3.jpg', alt='Image 3', url='https://example.com'),
        Card(title='Card 4', image_url='https://example.com/image4.jpg', alt='Image 4', url='https://example.com'),
    ])

def test_get_carousel(api_client, create_carousels):
    url = reverse('main_page:carousels-get-carousel')
    response = api_client.get(url, follow=True)
    assert response.status_code == 200
    assert response.data == CarouselSerializer(create_carousels, many=True).data

def test_get_card(api_client, create_cards):
    url = reverse('main_page:cards-get-card')
    response = api_client.get(url, follow=True)
    assert response.status_code == 200
    assert response.data == CardSerializer(create_cards, many=True).data