
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, ProfileSerializer
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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], url_path='authors-count', permission_classes=[])
    def authors_count(self, request):
        """
        Public endpoint to get total number of authors.
        URL: /api/users/authors-count/
        No authentication required.
        """
        count = self.queryset.filter(role='teacher').count()
        return Response({'count': count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='students-count', permission_classes=[])
    def students_count(self, request):
        """
        Public endpoint to get total number of authors.
        URL: /api/users/authors-count/
        No authentication required.
        """
        count = self.queryset.filter(role='student').count()
        return Response({'count': count}, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['get'], url_path='teachers', permission_classes=[AllowAny])
    def teachers(self, request):
        # Get all users with role='teacher'
        teachers = User.objects.filter(role='teacher').prefetch_related('courses')

        data = []
        for teacher in teachers:
            data.append({
                'id': teacher.id,
                'name': teacher.name,
                'avatar': teacher.avatar.url if teacher.avatar else None,
                'courses': [
                    {'id': course.id, 'title': course.title}
                    for course in teacher.courses.all()
                ]
            })

        return Response(data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logger.info("RegisterView POST hit!")

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])  # Hash password
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class LoginView(APIView):
    def post(self, request):

        email = request.data.get('email')
        password = request.data.get('password')


        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)  # Added 'request' for completeness

        if user is not None:
            # Use your custom serializer for token
            serializer = CustomTokenObtainPairSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is logged in

    def post(self, request):
        serializer = ProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)