from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Preferences, Route, Feedback
from unittest.mock import patch

class UserRegistrationTestCase(TestCase):
    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())
        self.assertTrue(Preferences.objects.filter(user__username='testuser').exists())

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')

    def test_login_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

class ProfileManagementTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        Preferences.objects.create(user=self.user, transportation_mode='PT', maximum_travel_time=60, maximum_cost=20.00, environmental_impact_preference='Low')

    def test_update_profile(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile'), {
            'email': 'newemail@example.com',
            'first_name': 'New',
            'last_name': 'Name',
            'transportation_mode': 'RS',
            'maximum_travel_time': 30,
            'maximum_cost': 10.00,
            'environmental_impact_preference': 'Medium'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.first_name,

 'New')
        self.assertEqual(self.user.last_name, 'Name')
        self.user.preferences.refresh_from_db()
        self.assertEqual(self.user.preferences.transportation_mode, 'RS')
        self.assertEqual(self.user.preferences.maximum_travel_time, 30)
        self.assertEqual(self.user.preferences.maximum_cost, 10.00)

class RoutePlanningTestCase(TestCase):
    @patch('requests.get')
    def test_route_suggestions(self, mock_get):
        mock_get.return_value.json.return_value = {
            'routes': ['Route 1', 'Route 2']
        }
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        Preferences.objects.create(user=user, transportation_mode='PT', maximum_travel_time=60, maximum_cost=20.00, environmental_impact_preference='Low')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('suggestions', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Route 1')
        self.assertContains(response, 'Route 2')

class FeedbackTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        self.route = Route.objects.create(user=self.user, origin='Point A', destination='Point B', route_details='Details', estimated_time=30, estimated_cost=15.00)

    def test_submit_feedback(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('feedback'), {
            'route': self.route.id,
            'feedback_comments': 'Great route!',
            'rating': 5
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Feedback.objects.filter(user=self.user, route=self.route, feedback_comments='Great route!', rating=5).exists())

class RealTimeUpdatesTestCase(TestCase):
    @patch('requests.get')
    def test_real_time_updates(self, mock_get):
        mock_get.return_value.json.return_value = {
            'status': 'ok',
            'updates': [
                {'message': 'Delay on line 1', 'time': '10:00 AM'},
                {'message': 'Service resumed on line 2', 'time': '10:15 AM'}
            ]
        }
        response = self.client.get(reverse('real_time_updates'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delay on line 1')
        self.assertContains(response, 'Service resumed on line 2')

class IntegrationWithAPITestCase(TestCase):
    @patch('requests.get')
    def test_integration_with_external_apis(self, mock_get):
        mock_get.return_value.json.return_value = {
            'status': 'ok',
            'data': {
                'routes': ['Route 1', 'Route 2']
            }
        }
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        Preferences.objects.create(user=user, transportation_mode='PT', maximum_travel_time=60, maximum_cost=20.00, environmental_impact_preference='Low')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('suggestions', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Route 1')
        self.assertContains(response, 'Route 2')

class PerformanceTestCase(TestCase):
    def test_system_performance(self):
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        Preferences.objects.create(user=user, transportation_mode='PT', maximum_travel_time=60, maximum_cost=20.00, environmental_impact_preference='Low')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('suggestions', args=[user.id]))
        self.assertEqual(response.status_code, 200)

class SecurityTestCase(TestCase):
    def test_user_data_encryption(self):
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123', first_name='Test', last_name='User')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

    def test_sql_injection_protection(self):
        response = self.client.post(reverse('login'), {
            'username': "' OR 1=1; --",
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_cross_site_scripting_protection(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile'), {
            'email': '<script>alert("XSS")</script>',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert("XSS")</script>')
