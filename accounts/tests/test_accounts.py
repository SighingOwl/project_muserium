# tests.py
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import User

# LoginAPIViewTest
class LoginAPIViewTest(APITestCase):
    def setUp(self):
        # URL for the login API
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')

        # Create a user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'PassWord!123',
            'username': 'TestUser',
            'name': 'TestUser',
            'mobile': '01012345678'
        }
        self.client.post(self.register_url, self.user_data, format='json')

    def test_login_success(self):
        data = {'email': 'test@example.com', 'password': 'PassWord!123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_failure(self):
        data = {'email': 'wrong@example.com', 'password': 'PassWord!123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

        data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

# LogoutAPIViewTest
class LogoutAPIViewTest(APITestCase):
    def setUp(self):
        # URL for the logout API
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')

        # Create a user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'PassWord!123',
            'username': 'TestUser',
            'name': 'TestUser',
            'mobile': '01012345678'
        }
        self.client.post(self.register_url, self.user_data, format='json')

        # Login the user
        data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        response = self.client.post(self.login_url, data, format='json')
        self.access_token = response.data['access']
    
    def test_logout_success(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.client.post(self.logout_url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

# NaverLoginAPIViewTest
class NaverLoginTests(APITestCase):
    
    @patch('requests.get')
    def test_naver_login_redirect(self, mock_get):
        naver_login_url = reverse('accounts:naver-login')
        response = self.client.get(naver_login_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('https://nid.naver.com/oauth2.0/authorize', response.url)

    @patch('requests.get')
    def test_naver_callback(self, mock_get):
        # Mock the response from Naver
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token'
        }
        
        naver_callback_url = reverse('accounts:naver-callback')
        response = self.client.get(naver_callback_url, {'code': 'mock_code', 'state': 'mock_state'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('access_token=mock_access_token', response.url)

    @patch('accounts.views.requests.get')
    @patch('accounts.views.requests.post')
    def test_login_to_django(self, mock_post, mock_get):    # 데코레이터와 매개변수의 순서는 반대임을 주
        # Create a user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

        # Mock the response from Naver
        mock_get_response = mock_get.return_value
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'response': {
                'id': 'mock_naver_id',
                'email': 'test@example.com',
                'mobile': '010-1234-5678',
                'mobile_e164': '+821012345678',
                'name': 'Test User',
            }
        }
        
        # Mock the response from Django
        mock_post_response = mock_post.return_value
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            'access': 'mock_access_token',
            'refresh': 'mock_refresh_token'
        }
        
        # URL for the login to Django API
        login_to_django_url = reverse('accounts:login-to-django-login')


        data = {
            'access_token': 'mock_access_token',
            'code': 'mock_code'
        }        
        response = self.client.post(login_to_django_url, data, format='json', follow=True)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @patch('requests.get')
    def test_naver_user_data(self, mock_get):
        # Create a user
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=user)
        
        # Mock the response from Naver
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'id': 'mock_naver_id',
                'email': 'test@example.com',
                'mobile': '010-1234-5678',
                'mobile_e164': '+821012345678',
                'name': 'Test User'
            }
        }
        
        naver_userdata_url = reverse('accounts:naver-userdata-get')
        response = self.client.get(naver_userdata_url, QUERY_STRING=f'naver_token=mock_access_token', format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['mobile'], '010-1234-5678')
        self.assertEqual(response.data['name'], 'Test User')


# User Account API Tests
class UserManagerTests(TestCase):
    def setUp(self):
        self.user_manager = User.objects

    def test_create_user(self):
        user = self.user_manager.create_user(username='testuser', email='test@example.com', password='password123')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_create_user_no_username(self):
        with self.assertRaises(TypeError):
            self.user_manager.create_user(username=None, email='test@example.com', password='password123')

    def test_create_user_no_email(self):
        with self.assertRaises(TypeError):
            self.user_manager.create_user(username='testuser', email=None, password='password123')

    def test_create_superuser(self):
        superuser = self.user_manager.create_superuser(username='admin', email='admin@example.com', password='password123')
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

class RegisterAPIViewTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', name='Test User', username='TestUser', password='PassWord!123', mobile='01012345678')

        # URL for the register API
        self.register_url = reverse('accounts:register')

    def test_register_success(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'PassWord!123',
            'username': 'NewUser',
            'name': 'New User',
            'mobile': '01012345679'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register_missing_values(self):
        data = {'email': 'newuser@example.com'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_invalid_email(self):
        data = {'email': 'newuser', 'password': 'PassWord!123','username': 'NewUser','name': 'New User', 'mobile': '01012345677'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_invalid_mobile(self):
        data = {'email': 'test1@example.com', 'password': 'PassWord!123','username': 'NewUser','name': 'New User', 'mobile': '12345678999'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_invalid_password(self):
        data = {'email': 'test1@example.com', 'password': 'password','username': 'NewUser','name': 'New User', 'mobile': '01012345677'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_existing_email(self):
        data = {'email': 'test@example.com', 'password': 'PassWord!123','username': 'NewUser','name': 'New User', 'mobile': '01012345677'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_existing_mobile(self):
        data = {'email': 'test1@example.com', 'password': 'PassWord!123','username': 'NewUser','name': 'New User', 'mobile': '01012345678'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class UpdateUserAPIViewTest(APITestCase):
    def setUp(self):
        # URL for the update user API
        self.register_url = reverse('accounts:register')
        self.update_user_url = reverse('accounts:update-user')

        # Create a user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'PassWord!123',
            'username': 'TestUser',
            'name': 'TestUser',
            'mobile': '01012345678'
        }
        self.client.post(self.register_url, self.user_data, format='json')
        self.user = User.objects.get(email=self.user_data['email'])
        self.client.force_authenticate(user=self.user)

    def test_update_user_success(self):
        data = {'mobile': '01087654321', 'name': 'New Name'}
        headers = {
            'current_password': self.user_data['password'],
            'new_password': 'pAsswOrd!123'
        }
        response = self.client.post(self.update_user_url, data, format='json', headers=headers, QUERY_STRING=f'email={self.user.email}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_invalid_mobile(self):
        # Invalid mobile number
        data = {'mobile': '12345678999'}
        response = self.client.post(self.update_user_url, data, format='json', QUERY_STRING=f'email={self.user.email}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_user_invalid_password(self):
        # Invalid password
        data = {'mobile': '01087654321'}
        headers = {
            'current_password': self.user_data['password'],
            'new_password': 'password'
        }
        response = self.client.post(self.update_user_url, data, format='json', headers=headers, QUERY_STRING=f'email={self.user.email}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_user_incorrect_current_password(self):
        # Incorrect current password
        data = {'mobile': '01087654321'}
        headers = {
            'current_password': 'wrongpassword',
            'new_password': 'pAsswOrd!123'
        }
        response = self.client.post(self.update_user_url, data, format='json', headers=headers, QUERY_STRING=f'email={self.user.email}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_user_unknown_user(self):
        data = {'mobile': '01087654321'}
        response = self.client.post(self.update_user_url, data, format='json', QUERY_STRING=f'email="wrong@exampel.com"')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
    
    def test_update_user_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'mobile': '01087654321'}
        response = self.client.post(self.update_user_url, data, format='json' ,QUERY_STRING=f'email={self.user.email}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

class CheckEmailAPIViewTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', username='TestUser', password='password123')

        # URL for the check email API
        self.url = reverse('accounts:check-email')

    def test_check_email_exists(self):
        response = self.client.get(self.url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['exists'])

    def test_check_email_not_exists(self):
        response = self.client.get(self.url, {'email': 'notexists@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['exists'])

    def test_check_email_missing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class RestoreEmailTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', name='Test User', username='TestUser', mobile='01012345678', password='PassWord!123')

        # URL for the restore email API
        self.restore_email_url = reverse('accounts:restore-email')
        
    def test_restore_email_success(self):
        data = {'name': 'Test User', 'mobile': '01012345678'}
        response = self.client.post(self.restore_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_restore_email_unknown_user(self):
        data = {'name': 'Wrong User', 'mobile': '01012345678'}
        response = self.client.post(self.restore_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_restore_email_missing_name(self):
        data = {'mobile': '01012345678'}
        response = self.client.post(self.restore_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_restore_email_missing_mobile(self):
        data = {'name': 'Test User'}
        response = self.client.post(self.restore_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class ResetPasswordTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', name='Test User', password='password123', username='TestUser')

        # URL for the reset password API
        self.reset_password_url = reverse('accounts:reset-password')

    def test_reset_password_success(self):
        data = {'email': self.user.email, 'name': self.user.name}
        response = self.client.post(self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('password', response.data)

    def test_reset_password_unknown_user(self):
        data = {'email': 'wrong@example.com', 'name': self.user.name}
        response = self.client.post(self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_reset_password_missing_email(self):
        data = {'name': self.user.name}
        response = self.client.post(self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_reset_password_missing_name(self):
        data = {'email': self.user.email}
        response = self.client.post(self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class IsAdminTest(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='test@example.com', username='TestUser', password='PassWord!123')
        self.admin_user = User.objects.create_user(email='admin@example.com', password='Admin!123', username='AdminUser', is_superuser=True)

        # URL for the is_admin API
        self.is_admin_url = reverse('accounts:is-admin')

    def test_is_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.is_admin_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_admin'])

    def test_is_not_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.is_admin_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_admin'])

    def test_is_not_authenticated(self):
        response = self.client.get(self.is_admin_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)