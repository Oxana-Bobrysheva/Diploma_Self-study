from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Material, Test, TestResult, Enrollment
from .serializers import CourseSerializer, MaterialSerializer, TestSerializer, TestResultSerializer, EnrollmentSerializer
from .permissions import IsTeacherOrAdmin, IsOwnerOrAdmin, IsStudentOrSubscribed

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]  # Students can view subscribed

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Auto-set owner to current user

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
        role = request.user.role  # Directly from your custom User model

        if role == 'teacher':
            # For teachers: Owned courses (with materials for completeness)
            courses = Course.objects.filter(owner=request.user).prefetch_related('materials')
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "teacher", "courses": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            # For students (or admins defaulting to student view): Enrolled courses (with materials)
            enrollments = Enrollment.objects.filter(user=request.user).select_related('course').prefetch_related('course__materials')
            courses = [enrollment.course for enrollment in enrollments]
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
