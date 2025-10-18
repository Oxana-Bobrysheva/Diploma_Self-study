from rest_framework.permissions import BasePermission

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['teacher', 'admin']

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.role == 'admin'

class IsStudentOrSubscribed(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Students can view if subscribed; teachers/admins always
        if request.user.role in ['teacher', 'admin']:
            return True
        return obj.subscriptions.filter(user_sub=request.user).exists()
