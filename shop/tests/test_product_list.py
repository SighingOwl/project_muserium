import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from shop.models import Product
from accounts.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_products(db):
    user = User.objects.create(username="testuser", password="password")
    Product.objects.create(
        title="Product 1",
        short_description="Short description 1",
        price=100,
        discount_rate=10,
        image_url="https://example.com/image1.jpg",
        image_alt="Image 1",
        likes=10,
        reviews=5,
        total_rating=50,
        average_rating=4.5,
        questions=2,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        purchased_by=user
    )
    Product.objects.create(
        title="Product 2",
        short_description="Short description 2",
        price=200,
        discount_rate=20,
        image_url="https://example.com/image2.jpg",
        image_alt="Image 2",
        likes=20,
        reviews=10,
        total_rating=40,
        average_rating=4.0,
        questions=4,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        purchased_by=user
    )
    Product.objects.create(
        title="Product 3",
        short_description="Short description 3",
        price=300,
        discount_rate=30,
        image_url="https://example.com/image3.jpg",
        image_alt="Image 3",
        likes=30,
        reviews=15,
        total_rating=30,
        average_rating=3.5,
        questions=6,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        purchased_by=user
    )
    Product.objects.create(
        title="Product 4",
        short_description="Short description 4",
        price=400,
        discount_rate=40,
        image_url="https://example.com/image4.jpg",
        image_alt="Image 4",
        likes=40,
        reviews=20,
        total_rating=20,
        average_rating=3.0,
        questions=8,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        purchased_by=user
    )
    Product.objects.create(
        title="Product 5",
        short_description="Short description 5",
        price=500,
        discount_rate=50,
        image_url="https://example.com/image5.jpg",
        image_alt="Image 5",
        likes=50,
        reviews=25,
        total_rating=10,
        average_rating=2.5,
        questions=10,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        purchased_by=user
    )

@pytest.mark.django_db
def test_list_products(api_client, create_products):
    url = reverse('shop:products-list-products')
    response = api_client.get(url, {'sort_by': '-created_at'}, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5

@pytest.mark.django_db
def test_list_products_invalid_sort(api_client, create_products):
    url = reverse('shop:products-list-products')
    response = api_client.get(url, {'sort_by': 'invalid_sort'}, follow=True)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == '잘못된 정렬 기준입니다.'

@pytest.mark.django_db
def test_list_top_products(api_client, create_products):
    url = reverse('shop:products-list-top-products')
    response = api_client.get(url, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4
    assert response.data[0]['likes'] >= response.data[1]['likes']