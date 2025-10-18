from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Payment, Subscription
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'city', 'avatar', 'role']

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
