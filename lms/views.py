from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Material, Test, TestResult, Enrollment
from .serializers import CourseSerializer, MaterialSerializer, TestSerializer, TestResultSerializer, EnrollmentSerializer
from .permissions import IsTeacherOrAdmin, IsOwnerOrAdmin, IsStudentOrSubscribed

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('materials').all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]

        if self.action in ['create', 'update', 'partial_update', 'destroy', 'edit']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin(), IsOwnerOrAdmin()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated(),
                IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Auto-set owner to current user

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
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course, owner=request.user)  # Link to course and set owner
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]  # Users can only see their own results

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)  # Filter to user's results

class MyCoursesView(APIView):
    """
    GET: Returns user's courses based on role.
    - Students: Enrolled courses.
    - Teachers: Owned courses.
    """
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
    """
    POST: Enrolls the authenticated user in a specific course.
    Body: Empty (course_id from URL).
    """
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
            # Check if user is enrolled in the course
            if not Enrollment.objects.filter(user=request.user, course=test.material.course).exists():
                return Response({"error": "Not enrolled in this course."}, status=403)
            answers = request.data.get('answers', {})
            # Validate and score (implement logic here)
            score = calculate_score(test.questions, answers)
            passed = score >= 70  # Example threshold
            TestResult.objects.create(user=request.user, test=test, answers=answers, score=score, passed=passed)
            return Response({"score": score, "passed": passed}, status=201)
        except Test.DoesNotExist:
            return Response({"error": "Test not found."}, status=404)
