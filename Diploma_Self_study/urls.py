from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from lms.views import dashboard
from users.views import register
from django.conf import settings
from django.conf.urls.static import static


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

    # path('test/', test_view, name='test'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)