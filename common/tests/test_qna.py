# tests/test_qna.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from common.models import GlassClass, Product, Question, Answer, User

class QnATests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(email="example@example.com", username='testuser', password='password')
        self.admin_user = User.objects.create_superuser(email="admin@example.com", username='admin', password='password')

        # Create Test Data
        self.glass_class = GlassClass.objects.create(title='Class 1', teacher='Teacher 1', category='Category 1', short_description='Short Description 1', price=10000, image_url='https://example.com/image1.jpg', image_alt='Image 1', likes=10, reviews=5, total_rating=25, average_rating=5, questions=0, created_at=timezone.now(), modified_at=timezone.now())
        self.product = Product.objects.create(title="Product 1", short_description="Short description 1", price=100, discount_rate=10, image_url="https://example.com/image1.jpg", image_alt="Image 1", likes=10, reviews=5, total_rating=50, average_rating=4.5, questions=0, created_at=timezone.now(), modified_at=timezone.now(),)
        self.question = Question.objects.create(title='Question 1', content='Test Question', author=self.user, glass_class=self.glass_class, created_at=timezone.now())
        self.answer = Answer.objects.create(author=self.admin_user, question=self.question, content='Test Answer', created_at=timezone.now())


        # Create a Test Image
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpg")
        self.bad_image = SimpleUploadedFile("test_image.js", b"file_content", content_type="script/js")
        
        # URL for the QnA APIs
        self.create_question_url = reverse('common:question-create-question')
        self.read_question_url = reverse('common:question-read-question')
        self.get_question_content_url = reverse('common:question-get-question-content')
        self.update_question_url = reverse('common:question-update-question')
        self.delete_question_url = reverse('common:question-delete-question')
        self.increase_question_view_count_url = reverse('common:question-increase-question-view-count')
        self.is_author_url = reverse('common:question-is-author')
        self.create_answer_url = reverse('common:answer-create-answer')
        self.update_answer_url = reverse('common:answer-update-answer')
        self.delete_answer_url = reverse('common:answer-delete-answer')

    # Create Question Test
    def test_create_question(self):
        self.client.force_authenticate(user=self.user)

        data = {'title': 'New Question', 'content': 'New Question', 'is_secret': False, 'image': self.image}
        response = self.client.post(self.create_question_url, data, format='multipart', QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'title': 'New Question', 'content': 'New Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.create_question_url, data, format='multipart', QUERY_STRING=f'product_id={self.product.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_question_no_permission(self):
        data = {'title': 'New Question', 'content': 'New Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.create_question_url, data, format='multipart', QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_create_question_no_class_id(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Question', 'content': 'New Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.create_question_url, data, format='multipart', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_question_bad_image(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Question', 'content': 'New Question', 'image': self.bad_image, 'is_secret': False}
        response = self.client.post(self.create_question_url, data, format='multipart', QUERY_STRING=f'class_id={self.glass_class.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


    # Read Question Test
    def test_read_question(self):
        response = self.client.get(self.read_question_url, {'class_id': self.glass_class.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.read_question_url, {'product_id': self.product.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_question_no_content_id(self):
        response = self.client.get(self.read_question_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_question_content(self):
        response = self.client.get(self.get_question_content_url, {'question_id': self.question.id}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_question_content_no_question_id(self):
        response = self.client.get(self.get_question_content_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Update Question Test
    def test_update_question(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Question', 'content': 'Updated Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.update_question_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_question_no_permission(self):
        data = {'title': 'Updated Question', 'content': 'Updated Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.update_question_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_update_question_no_question_id(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Question', 'content': 'Updated Question', 'image': self.image, 'is_secret': False}
        response = self.client.post(self.update_question_url, data, format='multipart', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_question_bad_image(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Question', 'content': 'Updated Question', 'image': self.bad_image, 'is_secret': False}
        response = self.client.post(self.update_question_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Delete Question Test
    def test_delete_question(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_question_url, QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Extra Question Test
    def test_increase_question_view_count(self):
        response = self.client.post(self.increase_question_view_count_url, QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_increase_question_view_count_no_question_id(self):
        response = self.client.post(self.increase_question_view_count_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_is_author(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.is_author_url, QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_is_author_no_permission(self):
        response = self.client.get(self.is_author_url, QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_is_author_no_question_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.is_author_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Create Answer Test
    def test_create_answer(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'New Answer', 'image': self.image}
        response = self.client.post(self.create_answer_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_answer_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'content': 'New Answer', 'image': self.image}
        response = self.client.post(self.create_answer_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_create_answer_no_question_id(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'New Answer', 'image': self.image}
        response = self.client.post(self.create_answer_url, data, format='multipart', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_answer_bad_image(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'New Answer', 'image': self.bad_image}
        response = self.client.post(self.create_answer_url, data, format='multipart', QUERY_STRING=f'question_id={self.question.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Update Answer Test
    def test_update_answer(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'Updated Answer', 'image': self.image}
        response = self.client.post(self.update_answer_url, data, format='multipart', QUERY_STRING=f'answer_id={self.answer.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_answer_no_permission(self):
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Updated Answer', 'image': self.image}
        response = self.client.post(self.update_answer_url, data, format='multipart', QUERY_STRING=f'answer_id={self.answer.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_update_answer_no_answer_id(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'Updated Answer', 'image': self.image}
        response = self.client.post(self.update_answer_url, data, format='multipart', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_answer_bad_image(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'content': 'Updated Answer', 'image': self.bad_image}
        response = self.client.post(self.update_answer_url, data, format='multipart', QUERY_STRING=f'answer_id={self.answer.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)    

    # Delete Answer Test
    def test_delete_answer(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.delete_answer_url, QUERY_STRING=f'answer_id={self.answer.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_answer_no_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_answer_url, QUERY_STRING=f'answer_id={self.answer.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_delete_answer_no_answer_id(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.delete_answer_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)