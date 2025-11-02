from django.urls import path

from . import views
from .views import CourseViewSet, course_detail_template, MaterialViewSet

urlpatterns = [
    # API URLs (for diploma requirements)
    path('api/courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='api-course-list'),
    path('api/materials/', MaterialViewSet.as_view({'get': 'list'}), name='api-material-list'),

    # Custom actions for CourseViewSet
    path('api/courses/<int:pk>/edit/', CourseViewSet.as_view({'patch': 'edit'}),
         name='api-course-edit'),
    path('api/courses/<int:pk>/add-material/', CourseViewSet.as_view({'post': 'add_material'}),
         name='api-course-add-material'),

    path('authors/', views.authors, name='authors'),
    path('discussions/', views.discussions, name='discussions'),
    path('author/<int:teacher_id>/courses/', views.author_courses, name='author_courses'),

    # Template URLs (for actual user interface)
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:course_id>/delete/', views.CourseDeleteView.as_view(),
         name='course-delete-template'),
    path('courses/<int:course_id>/', views.course_detail_template, name='course-detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course_template, name='enroll_course_template'),
    path('courses/<int:course_id>/edit/', views.CourseEditView.as_view(), name='course-edit-template'),
    path('profile/', views.profile, name='profile'),
    path('courses/create/', views.course_create, name='course_create'),
    path('materials/<int:material_id>/', views.MaterialDetailView.as_view(), name='material-detail'),

    # Swagger documentation
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

