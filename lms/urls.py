from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (CourseViewSet, MaterialViewSet, TestResultView, TestingViewSet,
                    QuestionViewSet, EnrollmentViewSet)

router = DefaultRouter()
router.register(r'tests', TestingViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    # API URLs (for diploma requirements)
    path('api/courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='api-course-list'),
    path('api/courses/<int:pk>/', views.CourseViewSet.as_view({'get': 'retrieve'}), name='api-course-detail'),
    path('api/materials/', MaterialViewSet.as_view({'get': 'list'}), name='api-material-list'),
    path('api/courses/<int:pk>/edit/', CourseViewSet.as_view({'patch': 'edit'}),
         name='api-course-edit'),
    path('api/courses/<int:pk>/add-material/', CourseViewSet.as_view({'post': 'add_material'}),
         name='api-course-add-material'),
    path('api/enroll/', views.EnrollCourseView.as_view(), name='api-enroll'),
    path('api/my-courses/', views.MyCoursesView.as_view(), name='api-my-courses'),

    # Dashboard management URLs
    path('authors/', views.authors, name='authors'),
    path('discussions/', views.discussions, name='discussions'),
    path('author/<int:teacher_id>/courses/', views.author_courses, name='author_courses'),
    path('profile/', views.profile, name='profile'),

    # Course management URLs
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:course_id>/delete/', views.CourseDeleteView.as_view(),
         name='course-delete-template'),
    path('courses/<int:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course_template,
         name='enroll_course_template'),
    path('courses/<int:course_id>/edit/', views.CourseEditView.as_view(),
         name='course-edit-template'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:course_id>/add-material/', views.MaterialCreateView.as_view(),
         name='material-create'),

    # Material management URLs
    path('materials/<int:material_id>/', views.MaterialDetailView.as_view(),
         name='material-detail'),
    path('courses/<int:course_id>/materials/<int:material_id>/edit/',
         views.MaterialEditView.as_view(), name='material-edit'),
    path('courses/<int:course_id>/materials/<int:material_id>/delete/',
         views.MaterialDeleteView.as_view(), name='material-delete'),

    # Testing management URLs
    path('materials/<int:material_id>/create-test/', views.TestingCreateView.as_view(),
         name='testing-create'),
    path('testing/<int:testing_id>/', views.TestingDetailView.as_view(),
         name='testing-detail'),
    path('testing/<int:testing_id>/update/', views.TestingUpdateView.as_view(),
         name='testing-update'),
    path('testing/<int:pk>/take/', views.TestTakeView.as_view(), name='test_take'),
    path('testing/<int:pk>/submit/', views.TestSubmitView.as_view(), name='test_submit'),
    path('attempt/<int:attempt_id>/result/', TestResultView.as_view(), name='test_result'),

    # Question management URLs
    path('testing/<int:testing_id>/questions/create/', views.QuestionCreateView.as_view(),
         name='create_question'),
    path('question/<int:pk>/update/', views.QuestionUpdateView.as_view(),
         name='update_question'),
    path('question/<int:pk>/delete/', views.QuestionDeleteView.as_view(),
         name='delete_question'),
]