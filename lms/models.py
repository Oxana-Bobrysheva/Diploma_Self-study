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
        'users.User',
        on_delete=models.CASCADE,
        related_name="courses_created",
        verbose_name="Автор курса",
        null=True,
        blank=True,
    )

    students = models.ManyToManyField(
        'users.User',
        through='Enrollment',
        related_name='enrolled_courses',
        blank=True
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
        'users.User',
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

class Testing(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name='testing')
    title = models.CharField(max_length=200, default="Тест к материалу")
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    time_limit = models.IntegerField(default=0, help_text="Лимит времени в минутах (0 - без лимита)")
    passing_score = models.IntegerField(default=70, help_text="Процент для успешной сдачи")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Test for {self.material.title}"


class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Текстовый вопрос'),
        ('text_image', 'Текст с изображением'),
        ('text_audio', 'Текст с аудио'),
        ('all', 'Текст, изображение и аудио'),
    ]

    testing = models.ForeignKey(Testing, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES, default='text')
    text = models.TextField(help_text="Текст вопроса")  # Always required
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    audio = models.FileField(upload_to='questions/audio/', blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."

    def clean(self):
        """Validate that required media fields are present based on question type"""
        from django.core.exceptions import ValidationError

        if self.question_type in ['text_image', 'all'] and not self.image:
            raise ValidationError({'image': 'Изображение обязательно для выбранного типа вопроса'})

        if self.question_type in ['text_audio', 'all'] and not self.audio:
            raise ValidationError({'audio': 'Аудио файл обязателен для выбранного типа вопроса'})


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}... ({'✓' if self.is_correct else '✗'})"


class Enrollment(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('student', 'course')  # Предотвращает повторные записи
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.email} записан на {self.course.title}"


class TestAttempt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    testing = models.ForeignKey(Testing, on_delete=models.CASCADE)
    score = models.FloatField(help_text="Percentage score")
    passed = models.BooleanField(default=False)
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.testing.title} - {self.score}%"