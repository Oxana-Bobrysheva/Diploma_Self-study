from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from lms.views import dashboard
from users.views import register

def test_view(request):
    return HttpResponse("Test view works!")

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication urls
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

    # App urls
    path('', dashboard, name='dashboard'),  # Main page
    path('lms/', include('lms.urls')),  # Your LMS app URLs
    path('users/', include('users.urls')),  # Your users app URLs

    path('test/', test_view, name='test'),
]

