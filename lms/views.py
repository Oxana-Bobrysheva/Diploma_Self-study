from rest_framework import viewsets, permissions
from .models import Course, Material, Test, TestResult
from .serializers import CourseSerializer, MaterialSerializer, TestSerializer, TestResultSerializer
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
