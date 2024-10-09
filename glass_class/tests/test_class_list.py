# tests/test_class_list.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from glass_class.models import GlassClass
from glass_class.serializers import ClassSerializer
import logging

logger = logging.getLogger(__name__)

class ClassListViewSetsTest(APITestCase):
    @classmethod
    def setUp(cls):
        # Create test data
        cls.class1 = GlassClass.objects.create(title='Class 1', teacher='Teacher 1', category='Category 1', short_description='Short Description 1', price=10000, image_url='https://example.com/image1.jpg', image_alt='Image 1', likes=10, reviews=5, total_rating=25, average_rating=5, questions=3, created_at=timezone.now(), modified_at=timezone.now())
        cls.class2 = GlassClass.objects.create(title='Class 2', teacher='Teacher 2', category='Category 2', short_description='Short Description 2', price=20000, image_url='https://example.com/image2.jpg', image_alt='Image 2', likes=20, reviews=10, total_rating=40, average_rating=4, questions=6, created_at=timezone.now(), modified_at=timezone.now())
        cls.class3 = GlassClass.objects.create(title='Class 3', teacher='Teacher 3', category='Category 3', short_description='Short Description 3', price=30000, image_url='https://example.com/image3.jpg', image_alt='Image 3', likes=30, reviews=15, total_rating=45, average_rating=3, questions=9, created_at=timezone.now(), modified_at=timezone.now())
        cls.class4 = GlassClass.objects.create(title='Class 4', teacher='Teacher 4', category='Category 4', short_description='Short Description 4', price=40000, image_url='https://example.com/image4.jpg', image_alt='Image 4', likes=40, reviews=20, total_rating=50, average_rating=2, questions=12, created_at=timezone.now(), modified_at=timezone.now())
        cls.class5 = GlassClass.objects.create(title='Class 5', teacher='Teacher 5', category='Category 5', short_description='Short Description 5', price=50000, image_url='https://example.com/image5.jpg', image_alt='Image 5', likes=50, reviews=25, total_rating=55, average_rating=1, questions=15, created_at=timezone.now(), modified_at=timezone.now())

        # URL for the class list API
        cls.list_classes_url = reverse('glass_class:class-list-classes')
        cls.list_top_classes_url = reverse('glass_class:class-list-top-classes')

    def test_list_classes(self):
        response = self.client.get(self.list_classes_url , {'sort_by': '-created_at', 'page_size': 5}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIn('total_pages', response.data)
        
    def test_list_classes_invalid_sort(self):
        response = self.client.get(self.list_classes_url, {'sort_by': 'invalid_field'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], '잘못된 정렬 기준입니다.')

    def test_list_top_classes(self):
        response = self.client.get(self.list_top_classes_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        sorted_classes = sorted([self.class1, self.class2, self.class3, self.class4, self.class5], key=lambda x: -x.likes)[:4]
        serializer = ClassSerializer(sorted_classes, many=True)
        self.assertEqual(response.data, serializer.data)