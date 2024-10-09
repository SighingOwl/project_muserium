# test_class_reservation.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from glass_class.models import GlassClass, Reservation
from datetime import datetime, timedelta

class ClassReservationTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Create a user
        self.user = User.objects.create_user(email='example@example.com', username='testuser', password='testpassword')
        self.user1 = User.objects.create_user(email='example1@example.com', username='testuser1', password='testpassword1')
        self.client.force_authenticate(user=self.user)

        # URL for the reservation APIs
        self.reservation_url = reverse('glass_class:reservation-create-reservation')
        self.list_reservations_url = reverse('glass_class:reservation-list-reservations')
        self.get_disabled_dates_url = reverse('glass_class:reservation-get-disabled-dates')
        self.get_disabled_timezones_url = reverse('glass_class:reservation-get-disabled-timezones')

        # Create a GlassClass data
        self.glass_class = GlassClass.objects.create(title='Test Class', description='Test Description', short_description='Test Short Description', duration=60, price=100, category='Test Category', image_url='https://example.com/image_1', image_alt='image 1', created_at=timezone.now(), modified_at=timezone.now())

        # Create reservation data
        Reservation.objects.create(glass_class=self.glass_class, user=self.user, reservation_date=timezone.now().date() + timedelta(days=1), reservation_time='10:00:00', created_at=timezone.now(), modified_at=timezone.now())
        Reservation.objects.create(glass_class=self.glass_class, user=self.user, reservation_date=timezone.now().date() + timedelta(days=1), reservation_time='12:00:00', created_at=timezone.now(), modified_at=timezone.now())
        Reservation.objects.create(glass_class=self.glass_class, user=self.user, reservation_date=timezone.now().date() + timedelta(days=1), reservation_time='14:00:00', created_at=timezone.now(), modified_at=timezone.now())

    def test_create_reservation(self):
        # login new user
        self.client.force_authenticate(user=self.user1)

        # Create a reservation
        data = {
            'class_id': self.glass_class.id,
            'reservation_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'reservation_time': '16:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_reservation_missing_class_id(self):
        data = {
            'reservation_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'reservation_time': '10:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_missing_reservation_date(self):
        data = {
            'class_id': self.glass_class.id,
            'reservation_time': '10:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_reservation_missing_reservation_time(self):
        data = {
            'class_id': self.glass_class.id,
            'reservation_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_invalid_reservation_date(self):
        data = {
            'class_id': self.glass_class.id,
            'reservation_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'reservation_time': '10:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_reservation_invalid_reservation_time(self):
        data = {
            'class_id': self.glass_class.id,
            'reservation_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'reservation_time': '11:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_duplicated_reservation(self):
        data = {
            'class_id': self.glass_class.id,
            'reservation_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'reservation_time': '10:00:00'
        }
        response = self.client.post(self.reservation_url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reservations(self):
        response = self.client.get(self.list_reservations_url, {'class_id': self.glass_class.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_list_reservations_missing_class_id(self):
        response = self.client.get(self.list_reservations_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_disabled_dates(self):
        response = self.client.get(self.get_disabled_dates_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_get_disabled_timezones(self):
        selected_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(self.get_disabled_timezones_url, {'selected_date': selected_date}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))