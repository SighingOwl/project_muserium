# tests/test_class_detail.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from glass_class.models import GlassClass
from accounts.models import User

class ClassDetailTests(APITestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='example@example.com', username='testuser', password='testpassword')
        
        # Create a GlassClass instance
        self.glass_class = GlassClass.objects.create(title='Test Class', description='Test Description', short_description='Test Short Description', duration=60, price=100, category='Test Category', image_url='https://example.com/image_1', image_alt='image 1', created_at=timezone.now(), modified_at=timezone.now())

        # URL for the class detail API
        self.get_class_detail_url = reverse('glass_class:class_detail-get-class-detail')

    def test_get_class_detail(self):
        # Log in the user
        self.client.login(email='example@example.com', password='testpassword')
        
        # Get the detail of the created class
        response = self.client.get(self.get_class_detail_url , {'id': self.glass_class.id}, follow=True)
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response data is correct
        self.assertEqual(response.data['title'], 'Test Class')
        self.assertEqual(response.data['description'], 'Test Description')
        self.assertEqual(response.data['short_description'], 'Test Short Description')
        self.assertEqual(response.data['duration'], 60)
        self.assertEqual(response.data['price'], 100)
        self.assertEqual(response.data['category'], 'Test Category')
        self.assertEqual(response.data['image_url'], 'https://example.com/image_1')
        self.assertEqual(response.data['image_alt'], 'image 1')
        self.assertEqual(response.data['likes'], 0)
        self.assertEqual(response.data['reviews'], 0)
        self.assertEqual(response.data['total_rating'], 0)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['questions'], 0)
        self.assertEqual(response.data['created_at'], timezone.localtime(self.glass_class.created_at).isoformat())
        self.assertEqual(response.data['modified_at'], timezone.localtime(self.glass_class.modified_at).isoformat())
        