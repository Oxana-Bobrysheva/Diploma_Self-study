import json

from django.http import JsonResponse
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny

from .models import Payment, Subscription
from .serializers import UserSerializer, PaymentSerializer, SubscriptionSerializer
from lms.permissions import IsOwnerOrAdmin
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """Custom action for /api/profiles/me/ - view/edit own profile."""
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # GET request
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)  # Only own payments

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user_sub=self.request.user)  # Only own subscriptions

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logger.info("RegisterView POST hit!")
        print("RegisterView POST hit!")  # Confirm view reached
        print("Request data:", request.data)  # See what's being sent
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])  # Hash password
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class LoginView(APIView):
    def post(self, request):
        print("=== LOGIN DEBUG ===")
        print("Request method:", request.method)
        print("Content-Type:", request.META.get('CONTENT_TYPE'))
        print("Request body:", request.body)  # Raw bytes—check if JSON is there
        print("User authenticated?", request.user.is_authenticated)  # Should be False

        # Use DRF's request.data for consistency (it parses JSON automatically)
        email = request.data.get('email')
        password = request.data.get('password')
        print("Extracted email:", email)
        print("Password provided?", bool(password))  # Don't log password for security

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)  # Added 'request' for completeness
        print("User found?", user is not None)
        if user is not None:
            # Use your custom serializer for token
            serializer = CustomTokenObtainPairSerializer(data=request.data)
            if serializer.is_valid():
                print("Serializer valid, returning token")
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Authentication failed")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
