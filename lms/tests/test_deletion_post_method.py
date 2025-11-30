from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from lms.models import Course, Material

User = get_user_model()


class MaterialDeleteViewTests(TestCase):
    """Comprehensive tests for material deletion post method"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create users
        self.superuser = User.objects.create_user(
            username='superuser',
            email='superuser@example.com',
            password='testpass123',
            name='Super User',
            role='teacher',
            is_superuser=True
        )

        self.course_owner = User.objects.create_user(
            username='courseowner',
            email='courseowner@example.com',
            password='testpass123',
            name='Course Owner',
            role='teacher'
        )

        self.material_owner = User.objects.create_user(
            username='materialowner',
            email='materialowner@example.com',
            password='testpass123',
            name='Material Owner',
            role='teacher'
        )

        self.other_teacher = User.objects.create_user(
            username='otherteacher',
            email='otherteacher@example.com',
            password='testpass123',
            name='Other Teacher',
            role='teacher'
        )

        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            name='Test Student',
            role='student'
        )

        # Create course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.course_owner,
            price=99.99
        )

        # Create material - using your actual model fields
        self.material = Material.objects.create(
            title='Test Material',
            content='Test Content',
            course=self.course,
            owner=self.material_owner
        )

        # URL for material deletion
        self.delete_url = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': self.material.id
        })

    def test_post_superuser_can_delete_any_material(self):
        """Test that superuser can delete any material"""
        self.client.force_login(self.superuser)

        response = self.client.post(self.delete_url)

        # Check material was deleted
        self.assertFalse(Material.objects.filter(id=self.material.id).exists())

        # Check redirect to course detail
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course.id}))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Материал "Test Material" успешно удален!')

    def test_post_course_owner_can_delete_material(self):
        """Test that course owner can delete materials from their course"""
        self.client.force_login(self.course_owner)

        response = self.client.post(self.delete_url)

        # Check material was deleted
        self.assertFalse(Material.objects.filter(id=self.material.id).exists())

        # Check redirect
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course.id}))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Материал "Test Material" успешно удален!')

    def test_post_material_owner_can_delete_own_material(self):
        """Test that material owner can delete their own material"""
        self.client.force_login(self.material_owner)

        response = self.client.post(self.delete_url)

        # Check material was deleted
        self.assertFalse(Material.objects.filter(id=self.material.id).exists())

        # Check redirect
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course.id}))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Материал "Test Material" успешно удален!')


    def test_post_anonymous_user_cannot_delete_material(self):
        """Test that anonymous users cannot delete materials"""
        response = self.client.post(self.delete_url)

        # Check material was NOT deleted
        self.assertTrue(Material.objects.filter(id=self.material.id).exists())

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_post_nonexistent_material_returns_404(self):
        """Test that deleting nonexistent material returns 404"""
        self.client.force_login(self.course_owner)

        invalid_url = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': 99999  # Nonexistent material
        })

        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_nonexistent_course_returns_404(self):
        """Test that deleting material from nonexistent course returns 404"""
        self.client.force_login(self.course_owner)

        invalid_url = reverse('material-delete', kwargs={
            'course_id': 99999,  # Nonexistent course
            'material_id': self.material.id
        })

        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_material_with_illustration_deletion(self):
        """Test deletion of material with associated illustration"""
        # Create a material with an illustration
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file content",
            content_type="image/jpeg"
        )

        image_material = Material.objects.create(
            title='Image Material',
            content='Image Content',
            course=self.course,
            owner=self.material_owner,
            illustration=test_image
        )

        image_delete_url = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': image_material.id
        })

        self.client.force_login(self.course_owner)
        response = self.client.post(image_delete_url)

        # Check material was deleted
        self.assertFalse(Material.objects.filter(id=image_material.id).exists())

        # Check redirect and success message
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course.id}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Материал "Image Material" успешно удален!')

    def test_post_multiple_materials_deletion_order(self):
        """Test that deleting one material doesn't affect others"""
        # Create additional materials
        material2 = Material.objects.create(
            title='Material 2',
            content='Content 2',
            course=self.course,
            owner=self.material_owner
        )

        material3 = Material.objects.create(
            title='Material 3',
            content='Content 3',
            course=self.course,
            owner=self.material_owner
        )

        self.client.force_login(self.course_owner)
        response = self.client.post(self.delete_url)

        # Check only the target material was deleted
        self.assertFalse(Material.objects.filter(id=self.material.id).exists())
        self.assertTrue(Material.objects.filter(id=material2.id).exists())
        self.assertTrue(Material.objects.filter(id=material3.id).exists())

        # Check redirect and success message
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course.id}))

    def test_post_material_title_in_success_message(self):
        """Test that success message contains the correct material title"""
        # Create material with special characters in title
        special_material = Material.objects.create(
            title='Материал с 🚀 специальными символами',
            content='Test Content',
            course=self.course,
            owner=self.material_owner
        )

        special_delete_url = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': special_material.id
        })

        self.client.force_login(self.course_owner)
        response = self.client.post(special_delete_url)

        # Check success message contains correct title
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Материал "Материал с 🚀 специальными символами" успешно удален!')


class MaterialDeletePermissionEdgeCases(TestCase):
    """Tests for edge cases in material deletion permissions"""

    def setUp(self):
        self.teacher1 = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            name='Teacher 1',
            role='teacher'
        )

        self.teacher2 = User.objects.create_user(
            username='teacher2',
            email='teacher2@example.com',
            password='testpass123',
            name='Teacher 2',
            role='teacher'
        )

        self.course1 = Course.objects.create(
            title='Course 1',
            description='Description 1',
            owner=self.teacher1,
            price=99.99
        )

        self.course2 = Course.objects.create(
            title='Course 2',
            description='Description 2',
            owner=self.teacher2,
            price=149.99
        )

        # Material owned by teacher1 in course1
        self.material1 = Material.objects.create(
            title='Material 1',
            content='Content 1',
            course=self.course1,
            owner=self.teacher1
        )

        # Material owned by teacher2 in course1 (co-teaching scenario)
        self.material2 = Material.objects.create(
            title='Material 2',
            content='Content 2',
            course=self.course1,
            owner=self.teacher2
        )

    def test_post_course_owner_can_delete_others_materials_in_their_course(self):
        """Test course owner can delete materials created by others in their course"""
        self.client.force_login(self.teacher1)  # Course owner

        delete_url = reverse('material-delete', kwargs={
            'course_id': self.course1.id,
            'material_id': self.material2.id  # Material owned by teacher2
        })

        response = self.client.post(delete_url)

        # Check material was deleted by course owner
        self.assertFalse(Material.objects.filter(id=self.material2.id).exists())
        self.assertRedirects(response, reverse('course-detail', kwargs={'course_id': self.course1.id}))


class MaterialDeleteIntegrationTests(TestCase):
    """Integration tests for material deletion"""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='testpass123',
            name='Test Teacher',
            role='teacher'
        )

        self.course = Course.objects.create(
            title='Integration Test Course',
            description='Integration Test Description',
            owner=self.teacher,
            price=99.99
        )

        # Create multiple materials
        self.materials = []
        for i in range(3):
            material = Material.objects.create(
                title=f'Material {i + 1}',
                content=f'Content {i + 1}',
                course=self.course,
                owner=self.teacher
            )
            self.materials.append(material)

    def test_post_delete_multiple_materials_sequentially(self):
        """Test deleting multiple materials sequentially"""
        self.client.force_login(self.teacher)

        # Delete first material
        delete_url1 = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': self.materials[0].id
        })

        response1 = self.client.post(delete_url1)
        self.assertFalse(Material.objects.filter(id=self.materials[0].id).exists())
        self.assertRedirects(response1, reverse('course-detail', kwargs={'course_id': self.course.id}))

        # Delete second material
        delete_url2 = reverse('material-delete', kwargs={
            'course_id': self.course.id,
            'material_id': self.materials[1].id
        })

        response2 = self.client.post(delete_url2)
        self.assertFalse(Material.objects.filter(id=self.materials[1].id).exists())
        self.assertRedirects(response2, reverse('course-detail', kwargs={'course_id': self.course.id}))

        # Verify third material still exists
        self.assertTrue(Material.objects.filter(id=self.materials[2].id).exists())

        # Check message counts
        messages = list(get_messages(response2.wsgi_request))
        # Should have 2 success messages (one from each deletion)
        self.assertEqual(len(messages), 2)