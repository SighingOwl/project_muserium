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
def create_product(db):
    user = User.objects.create(username="testuser", password="password")
    return Product.objects.create(
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

@pytest.mark.django_db
def test_get_product_detail(api_client, create_product):
    url = reverse('shop:product_detail-get-product-detail')
    response = api_client.get(url, {'id': create_product.id}, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == create_product.title
    assert response.data['price'] == create_product.price
    assert response.data['likes'] == create_product.likes
    assert response.data['average_rating'] == create_product.average_rating

@pytest.mark.django_db
def test_get_product_detail_no_id(api_client):
    url = reverse('shop:product_detail-get-product-detail')
    response = api_client.get(url, follow=True)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == '상품 id가 필요합니다.'