from django.urls import path

from . import views
from .views import CourseViewSet, course_list_template, course_detail_template

urlpatterns = [
    # API URLs (for diploma requirements)
    path('api/courses/', CourseViewSet.as_view({'get': 'list'}), name='api-course-list'),
    path('api/courses/<int:pk>/', CourseViewSet.as_view({'get': 'retrieve'}), name='api-course-detail'),

    path('authors/', views.authors, name='authors'),
    path('discussions/', views.discussions, name='discussions'),
    path('author/<int:teacher_id>/courses/', views.author_courses, name='author_courses'),

    # Template URLs (for actual user interface)
    path('courses/', views.course_list_template, name='course_list'),
    path('courses/<int:course_id>/', course_detail_template, name='course-detail'),
    path('my-courses/', views.my_courses_template, name='my_courses_template'),
    path('profile/', views.profile, name='profile'),

    # Swagger documentation
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

