from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import EnrollCourseView, MyCoursesView, SubmitTestView, CourseViewSet

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'test-results', views.TestResultViewSet)

urlpatterns = [
    path('courses/my/', MyCoursesView.as_view(), name='my-courses'),
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('courses/<int:pk>/edit/', CourseViewSet.as_view({'patch': 'edit'}), name='edit-course'),
    path('', include(router.urls)),
    path('submit-test/<int:test_id>/', SubmitTestView.as_view(), name='submit-test'),
]
