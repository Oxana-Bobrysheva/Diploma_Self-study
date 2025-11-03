from django.test import TestCase
from lms.forms import CourseForm
from lms.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()


class FormTests(TestCase):
    def test_course_form_valid(self):
        """Test CourseForm with valid data"""
        form_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'price': '0.00'  # ADD REQUIRED PRICE FIELD
        }
        form = CourseForm(data=form_data)

        if not form.is_valid():
            print("Form errors:", form.errors)

        self.assertTrue(form.is_valid())

    def test_course_form_invalid(self):
        """Test CourseForm with invalid data"""
        form_data = {
            'title': '',  # Title is required
            'description': 'Test Description',
            'price': '0.00'
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)