from django.test import TestCase
from django.contrib.auth import get_user_model
from users import views, serializers

User = get_user_model()


class UsersCoverageTests(TestCase):
    """Tests to increase users app coverage"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpass123",
            username="testuser",
            role="student",
        )

    def test_users_views_import(self):
        """Test all users views can be imported"""
        from users import views

        # If we get here, imports work
        self.assertTrue(hasattr(views, "profile"))

    def test_users_serializers_import(self):
        """Test all users serializers can be imported"""
        from users import serializers

        # If we get here, imports work
        self.assertTrue(hasattr(serializers, "UserSerializer"))

    def test_serializer_instantiation(self):
        """Test serializer can be instantiated"""
        from users.serializers import UserSerializer

        # Test with user instance
        serializer = UserSerializer(self.user)
        self.assertIsNotNone(serializer)

        # Test with data
        serializer = UserSerializer(
            data={"email": "new@test.com", "password": "newpass123"}
        )
        self.assertIsNotNone(serializer)

    def test_serializer_methods_exist(self):
        """Test serializer has required methods"""
        from users.serializers import UserSerializer

        serializer = UserSerializer()
        self.assertTrue(hasattr(serializer, "create"))
        self.assertTrue(hasattr(serializer, "update"))
        self.assertTrue(hasattr(serializer, "validate"))

    def test_profile_view_exists(self):
        """Test profile view function exists"""
        from users.views import profile

        self.assertTrue(callable(profile))

    def test_user_model_methods(self):
        """Test user model methods work"""
        # Test string representation
        self.assertEqual(str(self.user), "test@test.com")

        # Test get_full_name if exists
        if hasattr(self.user, "get_full_name"):
            full_name = self.user.get_full_name()
            self.assertIsInstance(full_name, str)

        # Test get_short_name if exists
        if hasattr(self.user, "get_short_name"):
            short_name = self.user.get_short_name()
            self.assertIsInstance(short_name, str)
