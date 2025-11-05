from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from lms.models import Course, Material, Testing, Question, Answer, TestAttempt
from lms.views import TestSubmitView

User = get_user_model()


class TestSubmitViewTests(TestCase):
    """Тесты для TestSubmitView"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            username='studentuser',
            role='student'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com',
            password='testpass123',
            username='teacheruser',
            role='teacher'
        )

        # Создаем тестовые данные
        self.course = Course.objects.create(title='Test Course', owner=self.teacher)
        self.material = Material.objects.create(
            title='Test Material',
            content='Test Content',
            course=self.course,
            owner=self.teacher
        )
        self.testing = Testing.objects.create(
            material=self.material,
            title='Test Quiz',
            passing_score=70
        )

        # Создаем вопросы и ответы
        self.question1 = Question.objects.create(
            testing=self.testing,
            text='What is 2+2?',
            question_type='text'
        )
        self.correct_answer1 = Answer.objects.create(
            question=self.question1,
            text='4',
            is_correct=True
        )
        self.wrong_answer1 = Answer.objects.create(
            question=self.question1,
            text='5',
            is_correct=False
        )

        self.question2 = Question.objects.create(
            testing=self.testing,
            text='What is 3+3?',
            question_type='text'
        )
        self.correct_answer2 = Answer.objects.create(
            question=self.question2,
            text='6',
            is_correct=True
        )
        self.wrong_answer2 = Answer.objects.create(
            question=self.question2,
            text='7',
            is_correct=False
        )

    def test_test_submit_view_partial_correct_answers(self):
        """Тест с частично правильными ответами"""
        # Отвечаем правильно только на первый вопрос
        post_data = {
            f'question_{self.question1.id}': self.correct_answer1.id,
            f'question_{self.question2.id}': self.wrong_answer2.id,  # Неправильный ответ
        }

        request = self.factory.post(reverse('test_submit', args=[self.testing.id]), post_data)
        request.user = self.student

        view = TestSubmitView()
        response = view.post(request, pk=self.testing.id)

        test_attempt = TestAttempt.objects.first()

        # 1 правильный ответ из 2 = 50%
        self.assertEqual(test_attempt.correct_answers, 1)
        self.assertEqual(test_attempt.score, 50.0)
        self.assertFalse(test_attempt.passed)  # 50% < 70% passing score

    def test_test_submit_view_no_answers(self):
        """Тест когда не отвечено ни на один вопрос"""
        post_data = {}  # Пустые ответы

        request = self.factory.post(reverse('test_submit', args=[self.testing.id]), post_data)
        request.user = self.student

        view = TestSubmitView()
        response = view.post(request, pk=self.testing.id)

        test_attempt = TestAttempt.objects.first()

        # 0 правильных ответов из 2 = 0%
        self.assertEqual(test_attempt.correct_answers, 0)
        self.assertEqual(test_attempt.score, 0.0)
        self.assertFalse(test_attempt.passed)

    def test_test_submit_view_invalid_answer_id(self):
        """Тест с невалидным ID ответа"""
        post_data = {
            f'question_{self.question1.id}': 'invalid_id',  # Невалидный ID
            f'question_{self.question2.id}': self.correct_answer2.id,
        }

        request = self.factory.post(reverse('test_submit', args=[self.testing.id]), post_data)
        request.user = self.student

        view = TestSubmitView()
        response = view.post(request, pk=self.testing.id)

        test_attempt = TestAttempt.objects.first()

        # Только один ответ должен быть засчитан (второй)
        self.assertEqual(test_attempt.correct_answers, 1)
        self.assertEqual(test_attempt.score, 50.0)

    def test_test_submit_view_nonexistent_answer(self):
        """Тест с несуществующим ID ответа"""
        post_data = {
            f'question_{self.question1.id}': 99999,  # Несуществующий ID
            f'question_{self.question2.id}': self.correct_answer2.id,
        }

        request = self.factory.post(reverse('test_submit', args=[self.testing.id]), post_data)
        request.user = self.student

        view = TestSubmitView()
        response = view.post(request, pk=self.testing.id)

        test_attempt = TestAttempt.objects.first()

        # Только один ответ должен быть засчитан
        self.assertEqual(test_attempt.correct_answers, 1)
        self.assertEqual(test_attempt.score, 50.0)
