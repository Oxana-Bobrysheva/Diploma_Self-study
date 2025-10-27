from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import EnrollCourseView, MyCoursesView

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'test-results', views.TestResultViewSet)

urlpatterns = [
    path('courses/my/', MyCoursesView.as_view(), name='my-courses'),
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('', include(router.urls)),
]
