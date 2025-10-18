from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'test-results', views.TestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
