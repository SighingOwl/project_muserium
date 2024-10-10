# tests.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from common.views import mask_username

class CommonTests(APITestCase):
    
    def test_get_csrf_token(self):
        url = reverse('common:get_csrf_token')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', response.json())

    def test_mask_username(self):
        self.assertEqual(mask_username('ab'), 'a*')
        self.assertEqual(mask_username('abc'), 'ab*')
        self.assertEqual(mask_username('abcd'), 'abc*')
        self.assertEqual(mask_username('abcde'), 'abcd*')
        self.assertEqual(mask_username('abcdef'), 'abcd**')