# 파일명: test_like.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from common.models import GlassClass, Product, Like, User
from django.utils import timezone

class LikeViewSetsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user
        self.user = User.objects.create_user(email='example@example.com', username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        # Create Test Data
        self.glass_class = GlassClass.objects.create(title='Class 1', teacher='Teacher 1', category='Category 1', short_description='Short Description 1', price=10000, image_url='https://example.com/image1.jpg', image_alt='Image 1', likes=0, reviews=5, total_rating=25, average_rating=5, questions=3, created_at=timezone.now(), modified_at=timezone.now())
        self.product = Product.objects.create(title="Product 1", short_description="Short description 1", price=100, discount_rate=10, image_url="https://example.com/image1.jpg", image_alt="Image 1", likes=0, reviews=5, total_rating=50, average_rating=4.5, questions=2, created_at=timezone.now(), modified_at=timezone.now(),)

        # URL for the like APIs
        self.like_class_url = reverse('common:like-like-class')
        self.is_like_class_url = reverse('common:like-is-like-class')
        self.like_product_url = reverse('common:like-like-product')
        self.is_like_product_url = reverse('common:like-is-like-product')

    def test_like_class(self):
        response = self.client.post(self.like_class_url, {'is_like': True}, format='json', QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.glass_class.refresh_from_db()
        self.assertEqual(self.glass_class.likes, 1)

        response = self.client.post(self.like_class_url, {'is_like': False}, format='json', QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.glass_class.refresh_from_db()
        self.assertEqual(self.glass_class.likes, 0)

    def test_is_like_class(self):
        response = self.client.get(self.is_like_class_url, QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_like'])

        Like.objects.create(user=self.user, glass_class=self.glass_class, created_at=timezone.now())
        response = self.client.get(self.is_like_class_url, QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_like'])

    def test_like_product(self):
        response = self.client.post(self.like_product_url, {'is_like': True}, format='json', QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.likes, 1)

        response = self.client.post(self.like_product_url, {'is_like': False}, format='json', QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.likes, 0)

    def test_is_like_product(self):
        response = self.client.get(self.is_like_product_url, QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_liked'])

        Like.objects.create(user=self.user, product=self.product, created_at=timezone.now())
        response = self.client.get(self.is_like_product_url, QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])