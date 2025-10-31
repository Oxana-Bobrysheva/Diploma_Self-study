from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CustomTokenObtainPairView
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    Welcome to the LMS API!<br>
    <a href="http://localhost:3000">Go to Frontend (React)</a><br>
    API endpoints: /api/ (e.g., /api/courses/)
    """)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('lms.urls')),
    path('api/users/', include('users.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
