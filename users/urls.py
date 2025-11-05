from django.urls import path
from . import views

urlpatterns = [
    # Template-based URLs
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.profile_update, name="profile_update"),
    # API endpoints if needed for AJAX
    path("api/teachers/", views.teachers_list_api, name="teachers_api"),
]
