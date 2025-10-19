from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Payment, Subscription
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  # Add for registration
    password_confirm = serializers.CharField(write_only=True, required=False)  # Optional: For confirmation

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'city', 'avatar', 'role', 'password', 'password_confirm']  # Added password fields
        read_only_fields = ['role']  # Keep role read-only; remove email from here so it can be set on registration
        extra_kwargs = {
            'password': {'write_only': True},
            'name': {'required': False},  # Make optional
            'phone': {'required': False},
            'city': {'required': False},
            'avatar': {'required': False},
            'password_confirm': {'required': False},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password_confirm and password != password_confirm:  # Only check if provided
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)  # Remove confirm field
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            **{k: v for k, v in validated_data.items() if k not in ['email', 'password']})
        return user

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Tell JWT to use email instead of username

    def validate(self, attrs):
        # Override to use email for authentication
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')
        return super().validate(attrs)
