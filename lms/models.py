from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    title = models.CharField(
        max_length=200, verbose_name="Курс", help_text="Введите название курса"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена курса",
        help_text="Укажите стоимость курса в рублях",
        default=0.00,
    )
    preview = models.ImageField(
        upload_to="courses/previews/",
        blank=True,
        null=True,
        verbose_name="Картинка",
        help_text="Загрузите картинку курса",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса",
        help_text="Расскажите о своём курсе",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Автор курса",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Material(models.Model):
    title = models.CharField(
        max_length=250, verbose_name="Материал", help_text="Введите название материала"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена материала",
        help_text="Укажите стоимость материала в рублях",
        default=0.00,
    )
    content = models.TextField(
        verbose_name="Содержание материала", help_text="Разместите текст или ссылку на файл"
    )

    illustration = models.ImageField(
        upload_to="materials/illustrations",
        blank=True,
        null=True,
        verbose_name="Иллюстрация",
        help_text="Загрузите иллюстрацию к материалу",
    )

    video_link = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Введите ссылку на видео",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Курс",
        help_text="Укажите курс",
        related_name="materials",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Автор материала",
        null=True,
        blank=True

    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["id"]

    def __str__(self):
        return self.title

class Test(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name='test')
    questions = models.JSONField()  # Структура: [{"question": "Текст?", "answers": ["A", "B", "C"], "correct": "A"}]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Преподаватель
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test for {self.material.title}"


class TestResult(models.Model):  # Результаты прохождения тестов
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_results', null=True, blank=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    answers = models.JSONField()  # Ответы пользователя: {"question1": "A", ...}
    score = models.FloatField()  # Процент правильных (0-100)
    passed = models.BooleanField(default=False)  # Пройден ли
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.material.title}: {self.score}%"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Студент",
        help_text="Пользователь, записавшийся на курс",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс",
        help_text="Курс, на который записан пользователь",
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата записи",
        help_text="Когда пользователь записался",
    )

    class Meta:
        unique_together = ('user', 'course')  # Предотвращает повторные записи
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user.email} записан на {self.course.title}"

