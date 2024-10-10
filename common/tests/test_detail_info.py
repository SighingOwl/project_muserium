# tests/test_detail_info.py
import json
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from common.models import GlassClass, Product, DetailInfo

class DetailInfoViewSetTests(APITestCase):
    def setUp(self):
        # Create a superuser
        self.user = User.objects.create_user(email="example@example.com", username='testuser', password='testpassword', is_superuser=True)
        self.client.login(email='example@example.com', password='testpassword')
        
        # Create test data
        self.glass_class = GlassClass.objects.create(title='Class 1', teacher='Teacher 1', category='Category 1', short_description='Short Description 1', price=10000, image_url='https://example.com/image1.jpg', image_alt='Image 1', likes=10, reviews=5, total_rating=25, average_rating=5, questions=3, created_at=timezone.now(), modified_at=timezone.now())
        self.product = Product.objects.create(title="Product 1", short_description="Short description 1", price=100, discount_rate=10, image_url="https://example.com/image1.jpg", image_alt="Image 1", likes=10, reviews=5, total_rating=50, average_rating=4.5, questions=2, created_at=timezone.now(), modified_at=timezone.now(),)
        self.detail_info = DetailInfo.objects.create(title='Detail Info 1', description_1='Description 1', description_2='Description 2', description_3='Description 3', product_image='https://example.com/image1.jpg', notice_image='https://example.com/image2.jpg', event_image='https://example.com/image3.jpg', glass_class=self.glass_class, product=self.product, created_at=timezone.now())
        
        # Create test an image
        self.image = SimpleUploadedFile("test_image.js", b"file_content", content_type="script/js")

        # URL for the detail info APIs
        self.get_detail_info_url = reverse('common:detail_info-get-detail-info')
        self.update_detail_info_url = reverse('common:detail_info-update-detail-info')

    def test_get_detail_info(self):
        response = self.client.get(self.get_detail_info_url, {'class_id': self.glass_class.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail_info', response.data)

    def test_get_detail_info_not_found(self):
        response = self.client.get(self.get_detail_info_url, {'class_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_update_detail_info(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'description_1': 'Updated Description 1',
            'description_2': 'Updated Description 2',
            'description_3': 'Updated Description 3',
        }
        response = self.client.post(self.update_detail_info_url, data, format='multipart', QUERY_STRING=f'detail_info_id={self.detail_info.id}',follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_update_detail_info_invalid_data_product_image(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'detail_info_id': self.detail_info.id,
            'product_image': self.image
        }
        response = self.client.post(self.update_detail_info_url, data, format='multipart', QUERY_STRING=f'detail_info_id={self.detail_info.id}',follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_detail_info_invalid_data_notice_image(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'detail_info_id': self.detail_info.id,
            'notice_image': self.image
        }
        response = self.client.post(self.update_detail_info_url, data, format='multipart', QUERY_STRING=f'detail_info_id={self.detail_info.id}',follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_detail_info_invalid_data_event_image(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'detail_info_id': self.detail_info.id,
            'event_image': self.image
        }
        response = self.client.post(self.update_detail_info_url, data, format='multipart', QUERY_STRING=f'detail_info_id={self.detail_info.id}',follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_detail_info_no_permission(self):
        self.client.force_authenticate(user=self.user)

        self.user.is_superuser = False
        self.user.save()
        response = self.client.post(self.update_detail_info_url, QUERY_STRING=f'detail_info_id={self.detail_info.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_update_detail_info_no_permission_logout(self):
        self.client.logout()
        response = self.client.post(self.update_detail_info_url, QUERY_STRING=f'detail_info_id={self.detail_info.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    