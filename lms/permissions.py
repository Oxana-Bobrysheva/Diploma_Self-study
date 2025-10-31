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
        return user.is_authenticated and (user.is_superuser or user.is_staff or user.role == 'teacher')

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Разрешаем доступ если пользователь - владелец объекта, админ или учитель
        if hasattr(obj, 'owner'):
            return (user.is_superuser or user.is_staff or
                    user.role == 'teacher' and user == obj.owner)
        return False


class IsCourseOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_superuser or user.is_staff or user.role == 'teacher')

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Для курсов - проверяем владельца курса
        if hasattr(obj, 'owner'):
            return (user.is_superuser or user.is_staff or
                    user.role == 'teacher' and user == obj.owner)
        # Для материалов - проверяем владельца курса материала
        elif hasattr(obj, 'course') and hasattr(obj.course, 'owner'):
            return (user.is_superuser or user.is_staff or
                    user.role == 'teacher' and user == obj.course.owner)
        return False


class IsStudentOrSubscribed(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем доступ всем аутентифицированным пользователям для просмотра
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Teachers/admins всегда имеют доступ
        if user.role in ['teacher', 'admin']:
            return True

        # Для студентов проверяем запись на курс
        if hasattr(obj, 'course'):
            course = obj.course
        elif hasattr(obj, 'material') and hasattr(obj.material, 'course'):
            course = obj.material.course
        else:
            return False

        # Используем Enrollment модель для проверки
        from .models import Enrollment
        return Enrollment.objects.filter(user=user, course=course).exists()