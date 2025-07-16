from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import CreateUserForm


class AccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_signup(self):
        """Test user registration functionality"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects after successful signup
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        """Test user login functionality"""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)  # Redirects after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_logout(self):
        """Test user logout functionality"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)  # Redirects after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_profile_view(self):
        """Test user profile view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_signup_form_validation(self):
        """Test signup form validation"""
        form_data = {
            "username": "testuser",  # Already exists
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = CreateUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser2",
                "email": "new2@example.com",
                "password1": "password123",
                "password2": "password456",  # Different password
            },
        )
        self.assertEqual(response.status_code, 200)  # Stays on signup page
        self.assertFalse(User.objects.filter(username="newuser2").exists())

    def test_signup_invalid_email(self):
        """Test signup with invalid email format"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser3",
                "email": "invalid-email",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertEqual(response.status_code, 200)  # Stays on signup page
        self.assertFalse(User.objects.filter(username="newuser3").exists())

    def test_profile_view_unauthorized(self):
        """Test accessing profile without login"""
        response = self.client.get(reverse("profile", args=[self.user.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_profile_view_wrong_user(self):
        """Test accessing another user's profile"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile", args=[other_user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_user_str_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), "testuser")

    def test_signup_short_password(self):
        """Test signup with short password"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser4",
                "email": "new4@example.com",
                "password1": "short",
                "password2": "short",
            },
        )
        self.assertEqual(response.status_code, 200)  # Stays on signup page
        self.assertFalse(User.objects.filter(username="newuser4").exists())
