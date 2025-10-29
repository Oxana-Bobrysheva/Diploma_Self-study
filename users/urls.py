from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ProfileUpdateView

router = DefaultRouter()
router.register(r'', views.UserViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'profiles', views.UserViewSet, basename='profile')

urlpatterns = [
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path(
        'teachers/',
        views.UserViewSet.as_view({'get': 'teachers'}),
        name='teachers'
    ),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('', include(router.urls)),
]
