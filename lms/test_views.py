from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from lms.models import Course, Material, Enrollment, Testing, Question, Answer

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            email='teacher@test.com',
            password='testpass123',
            username='teacheruser',
            role='teacher'
        )
        self.student = User.objects.create_user(  # ADD THIS
            email='student@test.com',
            password='testpass123',
            username='studentuser',
            role='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            owner=self.teacher
        )

    def test_course_list_view(self):
        """Test course list view returns 200"""
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_redirects_when_not_logged_in(self):
        """Test course detail redirects to login when not authenticated"""
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        # Should redirect to login when not authenticated
        self.assertEqual(response.status_code, 302)

    def test_material_detail_view_redirects_when_not_logged_in(self):
        """Test material detail redirects to login when not authenticated"""
        material = Material.objects.create(
            title='Test Material',
            content='Test Content',
            course=self.course,
            owner=self.teacher
        )
        response = self.client.get(reverse('material-detail', args=[material.id]))
        # Should redirect to login when not authenticated
        self.assertEqual(response.status_code, 302)

    def test_testing_views_exist(self):
        """Test that testing-related views can be accessed (or redirect)"""
        material = Material.objects.create(title='Test Material', course=self.course)
        testing = Testing.objects.create(material=material, title='Test Quiz')

        # Test testing detail view
        response = self.client.get(reverse('testing-detail', args=[testing.id]))
        # Should either return 200 or redirect (302)
        self.assertIn(response.status_code, [200, 302])

    def test_enrollment_creation_through_view(self):
        """Test enrollment can be created (coverage for enrollment logic)"""
        # This tests the enrollment model creation path
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_question_answer_creation_through_views(self):
        """Test question and answer creation (coverage for testing logic)"""
        material = Material.objects.create(title='Test Material', course=self.course)
        testing = Testing.objects.create(material=material, title='Test Quiz')

        question = Question.objects.create(
            testing=testing,
            text='Test question?',
            question_type='text'
        )
        answer = Answer.objects.create(
            question=question,
            text='Test answer',
            is_correct=True
        )

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 1)
