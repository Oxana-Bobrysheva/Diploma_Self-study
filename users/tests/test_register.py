from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from users.forms import UserRegistrationForm

User = get_user_model()


class RegisterViewTests(TestCase):
    """Comprehensive tests for the register view function"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Sample valid registration data - use email as username since that's what your model uses
        self.valid_registration_data = {
            'email': 'test@example.com',  # This is used as username in your model
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'name': 'Test User',
            'role': 'student'
        }

    def test_register_get_request_returns_form(self):
        """Test GET request returns registration form"""
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_register_post_valid_data_creates_user(self):
        """Test POST with valid data creates user and redirects"""
        user_count_before = User.objects.count()

        response = self.client.post(reverse('register'), data=self.valid_registration_data)

        user_count_after = User.objects.count()
        print(f"Users before: {user_count_before}, after: {user_count_after}")

        # User should be created
        self.assertEqual(user_count_after, user_count_before + 1)

        # Find user by email (which is the username in your model)
        user = User.objects.filter(email='test@example.com').first()
        self.assertIsNotNone(user, "User should be created with email as identifier")
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, 'student')

        # Check redirect to dashboard
        self.assertRedirects(response, reverse('dashboard'))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Регистрация прошла успешно!")

    def test_register_post_valid_data_logs_in_user(self):
        """Test that user is logged in after successful registration"""
        response = self.client.post(reverse('register'), data=self.valid_registration_data)

        # Check that user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Verify it's the correct user
        user = User.objects.get(email='test@example.com')
        self.assertEqual(response.wsgi_request.user, user)

    def test_register_post_invalid_data_returns_form_with_errors(self):
        """Test POST with invalid data returns form with errors"""
        invalid_data = {
            'email': 'invalid-email',  # Invalid email
            'password1': 'short',  # Too short
            'password2': 'different',  # Doesn't match
            'name': 'Test User',
            'role': 'student'
        }

        response = self.client.post(reverse('register'), data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('form', response.context)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)

    def test_register_post_missing_required_fields(self):
        """Test registration with missing required fields"""
        missing_data = {
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            # Missing name and role
        }

        response = self.client.post(reverse('register'), data=missing_data)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_register_post_password_mismatch(self):
        """Test registration with mismatched passwords"""
        mismatch_data = {
            'email': 'test@example.com',
            'password1': 'Password123!',
            'password2': 'DifferentPassword123!',  # Doesn't match
            'name': 'Test User',
            'role': 'student'
        }

        response = self.client.post(reverse('register'), data=mismatch_data)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_register_context_contains_form(self):
        """Test that context always contains form"""
        response = self.client.get(reverse('register'))
        self.assertIn('form', response.context)

        # Also test with POST that fails
        response = self.client.post(reverse('register'), data={})
        self.assertIn('form', response.context)

    def test_register_weak_password(self):
        """Test registration with weak password"""
        weak_password_data = {
            'email': 'test@example.com',
            'password1': '123',  # Too weak
            'password2': '123',
            'name': 'Test User',
            'role': 'student'
        }

        response = self.client.post(reverse('register'), data=weak_password_data)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class RegisterIntegrationTests(TestCase):
    """Integration tests for registration flow"""

    def test_complete_registration_flow(self):
        """Test complete user registration and login flow"""
        # Start unauthenticated
        self.assertFalse(self.client.session.get('_auth_user_id'))

        # Register new user
        registration_data = {
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'name': 'New User',
            'role': 'student'
        }

        response = self.client.post(reverse('register'), data=registration_data)

        # Check registration was successful
        self.assertRedirects(response, reverse('dashboard'))

        # Check user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.email, 'newuser@example.com')

        # Check user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Регистрация прошла успешно!")

        # Verify user can access protected page (dashboard)
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_registration_followed_by_logout_and_login(self):
        """Test that registered user can logout and login again"""
        # Register
        registration_data = {
            'email': 'login@example.com',
            'password1': 'LoginPass123!',
            'password2': 'LoginPass123!',
            'name': 'Login User',
            'role': 'student'
        }

        self.client.post(reverse('register'), data=registration_data)

        # Logout
        self.client.logout()
        self.assertFalse(self.client.session.get('_auth_user_id'))

        # Login with same credentials (using email as username)
        login_success = self.client.login(email='login@example.com', password='LoginPass123!')
        self.assertTrue(login_success)

        # Verify login worked
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)


class RegisterEdgeCaseTests(TestCase):
    """Tests for edge cases in registration"""

    def test_register_empty_post_data(self):
        """Test registration with empty POST data"""
        response = self.client.post(reverse('register'), data={})

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_register_with_special_characters_in_name(self):
        """Test registration with special characters in name"""
        special_char_data = {
            'email': 'special@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'name': 'Test User 🚀 with emoji',
            'role': 'student'
        }

        response = self.client.post(reverse('register'), data=special_char_data)

        # Should succeed
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='special@example.com')
        self.assertEqual(user.name, 'Test User 🚀 with emoji')


class RegisterFormInvestigationTests(TestCase):
    """Tests to verify form behavior"""

    def test_form_save_creates_user_correctly(self):
        """Test that form save creates user with correct fields"""
        form_data = {
            'email': 'formtest@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'name': 'Form Test User',
            'role': 'teacher'
        }

        form = UserRegistrationForm(data=form_data)

        self.assertTrue(form.is_valid(), f"Form should be valid but has errors: {form.errors}")

        user = form.save()

        # Verify user was created with correct data
        self.assertEqual(user.email, 'formtest@example.com')
        self.assertEqual(user.name, 'Form Test User')
        self.assertEqual(user.role, 'teacher')

        # Verify user exists in database and can be retrieved by email
        db_user = User.objects.get(email='formtest@example.com')
        self.assertEqual(db_user.name, 'Form Test User')
        self.assertTrue(db_user.check_password('TestPass123!'))