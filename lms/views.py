from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Material, Test, TestResult, Enrollment
from .serializers import CourseSerializer, MaterialSerializer, TestSerializer, TestResultSerializer, \
    EnrollmentSerializer
from .permissions import IsTeacherOrAdmin, IsCourseOwnerOrAdmin, IsStudentOrSubscribed


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('materials').all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]  # Все могут видеть список курсов
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated()]  # Аутентифицированные могут видеть детали
        elif self.action in ['create']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]  # Только учителя и админы могут создавать
        elif self.action in ['update', 'partial_update', 'destroy', 'edit', 'add_material']:
            return [permissions.IsAuthenticated(),
                    IsCourseOwnerOrAdmin()]  # Только владельцы и админы могут редактировать
        else:
            return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Автоматически устанавливаем владельца

    @action(detail=True, methods=['patch'], url_path='edit')
    def edit(self, request, pk=None):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add-material')
    def add_material(self, request, pk=None):
        course = self.get_object()
        print(f"DEBUG: Adding material - User: {request.user}, Course owner: {course.owner}")

        # Создаем копию данных и добавляем курс и владельца
        material_data = request.data.copy()

        serializer = MaterialSerializer(data=material_data)
        if serializer.is_valid():
            # Сохраняем материал с привязкой к курсу и текущему пользователю как владельцу
            material = serializer.save(
                course=course,
                owner=request.user
            )
            print(f"DEBUG: Material created successfully - ID: {material.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(f"DEBUG: Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCourseOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role

        if role == 'teacher':
            courses = Course.objects.filter(owner=request.user).prefetch_related('materials')
            print("Teacher courses found:", courses.count())
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "teacher", "courses": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            enrollments = Enrollment.objects.filter(user=request.user).select_related('course').prefetch_related(
                'course__materials')
            print("Student enrollments found:", enrollments.count())
            courses = [enrollment.course for enrollment in enrollments]
            print("Student courses found:", len(courses))
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "student", "courses": serializer.data},
                status=status.HTTP_200_OK
            )


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user,
                course=course
            )
            if created:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {"message": "Успешно записаны на курс!", "enrollment": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            else:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {"message": "Вы уже записаны на этот курс.", "enrollment": serializer.data},
                    status=status.HTTP_200_OK
                )
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND)


class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrSubscribed]

    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
            if not Enrollment.objects.filter(user=request.user, course=test.material.course).exists():
                return Response({"error": "Not enrolled in this course."}, status=403)

            # Простая функция для расчета баллов
            def calculate_score(questions, answers):
                correct = 0
                total = len(questions)
                for i, q in enumerate(questions):
                    if answers.get(str(i)) == q['correct']:
                        correct += 1
                return (correct / total) * 100 if total > 0 else 0

            answers = request.data.get('answers', {})
            score = calculate_score(test.questions, answers)
            passed = score >= 70
            TestResult.objects.create(user=request.user, test=test, answers=answers, score=score, passed=passed)
            return Response({"score": score, "passed": passed}, status=201)
        except Test.DoesNotExist:
            return Response({"error": "Test not found."}, status=404)