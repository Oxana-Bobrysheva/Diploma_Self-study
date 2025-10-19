from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.UserViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'profiles', views.UserViewSet, basename='profile')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
]
