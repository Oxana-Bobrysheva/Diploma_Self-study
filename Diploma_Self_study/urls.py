from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from lms.views import dashboard
from users.views import register
from django.conf import settings
from django.conf.urls.static import static


# Swagger/OpenAPI configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Self-Study Platform API",
        default_version='v1',
        description="API documentation for Self-Study Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@platform.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation - ADD THESE LINES:
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Optional: JSON schema
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

    # App urls
    path('', dashboard, name='dashboard'),  # Main page
    path('lms/', include('lms.urls')),  # Your LMS app URLs
    path('users/', include('users.urls')),  # Your users app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
