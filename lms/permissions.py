from rest_framework.permissions import BasePermission

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (user.is_authenticated and
                (user.is_superuser or user.is_staff or user.role == 'teacher'))

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user.is_superuser or user.is_staff or user.role == 'teacher')

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_superuser or user.is_staff)

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user.is_superuser or user.is_staff or user == obj.owner)


class IsStudentOrSubscribed(BasePermission):
    def has_permission(self, request, view):
        # General check: User must be a student
        return request.user and request.user.role == 'student'

    def has_object_permission(self, request, view, obj):
        # Teachers/admins always have access
        if request.user.role in ['teacher', 'admin']:
            return True
        # For students, check enrollment in the course
        # Handle different object types (Course, Material, Test)
        if hasattr(obj, 'course'):
            course = obj.course
        elif hasattr(obj, 'material') and hasattr(obj.material, 'course'):
            course = obj.material.course
        elif hasattr(obj, 'subscriptions'):
            return obj.subscriptions.filter(user_sub=request.user).exists()
        else:
            return False  # Can't determine course, deny access
        # Use Enrollment model for the check
        from .models import Enrollment  # Avoid circular imports
        return Enrollment.objects.filter(user=request.user, course=course).exists()
