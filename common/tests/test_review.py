# tests/test_review.py
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from common.models import GlassClass, Product, Review, User

class ReviewViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user
        self.user = User.objects.create_user(email='example@example.com', username='testuser', password='testpass')
        self.another_user = User.objects.create_user(email='example1@example.com', username='testuser1', password='testpass1')
        self.admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='adminpass')

        # Create the Test Data
        self.glass_class = GlassClass.objects.create(title='Class 1', teacher='Teacher 1', category='Category 1', short_description='Short Description 1', price=10000, image_url='https://example.com/image1.jpg', image_alt='Image 1', likes=10, reviews=1, total_rating=25, average_rating=5, questions=0, created_at=timezone.now(), modified_at=timezone.now())
        self.product = Product.objects.create(title="Product 1", short_description="Short description 1", price=100, discount_rate=10, image_url="https://example.com/image1.jpg", image_alt="Image 1", likes=10, reviews=1, total_rating=50, average_rating=4.5, questions=0, created_at=timezone.now(), modified_at=timezone.now(),)

        self.class_review = Review.objects.create(author=self.user, glass_class=self.glass_class, rating=5, sub_rating_1=5, sub_rating_2=5, sub_rating_3=5, content='Good class!', created_at=timezone.now())
        self.product_review = Review.objects.create(author=self.user, product=self.product, rating=4, sub_rating_1=4, sub_rating_2=4, sub_rating_3=4, content='Good product!', created_at=timezone.now())

        # Create a test image
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpg")
        self.bad_image = SimpleUploadedFile("bad_image.js", b"file_content", content_type="script/js")

        # URL for the review APIs
        self.create_review_url = reverse('common:review-create-review')
        self.read_review_url = reverse('common:review-read-review')
        self.update_review_url = reverse('common:review-update-review')
        self.delete_review_url = reverse('common:review-delete-review')
        

    # Test create review
    def test_create_review(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Create a class review
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 3)

        # Create a product review
        data = {'image': self.image, 'rating': 3, 'sub_rating_1': 1, 'sub_rating_2': 1, 'sub_rating_3': 1,'content': 'Good product!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 4)

    def test_create_review_unauthenticated(self):
        # Create a review without authentication

        # Create a class review
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)

        # Create a product review
        data = {'image': self.image, 'rating': 3, 'sub_rating_1': 1, 'sub_rating_2': 1, 'sub_rating_3': 1,'content': 'Good product!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)

    def test_create_review_invalid_id(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Create a review with an invalid class id
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING='glass_class_id=1000', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)

        # Create a review with an invalid product id
        data = {'image': self.image, 'rating': 3, 'sub_rating_1': 1, 'sub_rating_2': 1, 'sub_rating_3': 1,'content': 'Good product!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING='product_id=1000', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)

    def test_create_review_invalid_value(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Create a review with invalid rating value
        data = {'image': self.image, 'rating': 6, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

        # Create a review with invalid sub_rating_1 value
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 6, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

        # Create a review with invalid sub_rating_2 value
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 6, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

        # Create a review with invalid sub_rating_3 value
        data = {'image': self.image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 6,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

        # Create a review with invalid image
        data = {'image': self.bad_image, 'rating': 4, 'sub_rating_1': 2, 'sub_rating_2': 2, 'sub_rating_3': 2,'content': 'Good class!', 'created_at': timezone.now()}
        response = self.client.post(self.create_review_url, data, format='multipart', QUERY_STRING=f'glass_class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

    # Test read review
    def test_read_review(self):
        # Read the class review
        response = self.client.get(self.read_review_url, {'glass_class_id': self.glass_class.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reviews', response.data)

        # Read the product review
        response = self.client.get(self.read_review_url, {'product_id': self.product.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reviews', response.data)

    def test_read_review_invalid_id(self):
        response = self.client.get(self.read_review_url, {'glass_class_id': 1000}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

        response = self.client.get(self.read_review_url, {'product_id': 1000}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    # Test update review
    def test_update_review(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # New review data
        data = {
            'rating': 3,
            'sub_rating_1': 2,
            'sub_rating_2': 1,
            'sub_rating_3': 2,
            'content': 'Updated review',
            'image': self.image
        }

        # Update the class review
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 3)
        self.assertEqual(self.class_review.content, 'Updated review')

        # Update the product review
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.product_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_review.refresh_from_db()
        self.assertEqual(self.product_review.rating, 3)
        self.assertEqual(self.product_review.content, 'Updated review')

    def test_update_review_unauthenticated(self):
        # New review data
        data = {
            'rating': 3,
            'sub_rating_1': 2,
            'sub_rating_2': 1,
            'sub_rating_3': 2,
            'content': 'Updated review',
            'image': self.image
        }

        # Update the class review without authentication
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('detail', response.data)

    def test_update_review_admin(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.admin)

        # New review data
        data = {
            'rating': 3,
            'sub_rating_1': 2,
            'sub_rating_2': 1,
            'sub_rating_3': 2,
            'content': 'Updated review',
            'image': self.image
        }

        # Update the class review
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

        # Update the product review
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.product_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.product_review.refresh_from_db()
        self.assertEqual(self.product_review.rating, 4)
        self.assertEqual(self.product_review.content, 'Good product!')
        self.assertIn('error', response.data)

    def test_update_review_invalid_id(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # New review data
        data = {
            'rating': 3,
            'sub_rating_1': 2,
            'sub_rating_2': 1,
            'sub_rating_3': 2,
            'content': 'Updated review',
            'image': self.image
        }

        # Update the review with an invalid id
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING='review_id=1000', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_update_review_invalid_value(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # New review data
        data = {
            'rating': 6,
            'sub_rating_1': 2,
            'sub_rating_2': 1,
            'sub_rating_3': 2,
            'content': 'Updated review',
            'image': self.image
        }

        # Update the class review with invalid rating value
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

        # Update the class review with invalid sub_rating_1 value
        data = {
            'rating': 5,
            'sub_rating_1': 6,
        }
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

        # Update the class review with invalid sub_rating_2 value
        data = {
            'sub_rating_1': 1,
            'sub_rating_2': 6,
        }
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

        # Update the class review with invalid sub_rating_3 value
        data = {
            'sub_rating_2': 1,
            'sub_rating_3': 6,
        }
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

        # Update the class review with invalid image
        data = {
            'rating': 5,
            'image': self.bad_image
        }
        response = self.client.post(self.update_review_url, data, format='multipart', QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.class_review.refresh_from_db()
        self.assertEqual(self.class_review.rating, 5)
        self.assertEqual(self.class_review.content, 'Good class!')
        self.assertIn('error', response.data)

    # Test delete review
    def test_delete_review(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Delete the class review
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 1)

        # Delete the product review
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.product_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 0)
    
    def test_delete_review_admin(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.admin)

        # Delete the class review
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 1)

        # Delete the product review
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.product_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_unauthenticated(self):
        # Delete the review without authentication
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)

        # Delete the review from another user
        self.client.force_authenticate(user=self.another_user)
        response = self.client.delete(self.delete_review_url, QUERY_STRING=f'review_id={self.class_review.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('error', response.data)

    def test_delete_review_invalid_id(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Delete the review with an invalid id
        response = self.client.delete(self.delete_review_url, QUERY_STRING='review_id=1000', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Review.objects.count(), 2)
        self.assertIn('detail', response.data)
    
