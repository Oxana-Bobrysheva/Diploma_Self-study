from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )  # Add for registration
    password_confirm = serializers.CharField(
        write_only=True, required=False
    )  # Optional: For confirmation

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "city",
            "avatar",
            "role",
            "password",
            "password_confirm",
        ]  # Added password fields
        read_only_fields = [
            "role"
        ]  # Keep role read-only; remove email from here so it can be set on registration
        extra_kwargs = {
            "password": {"write_only": True},
            "name": {"required": False},  # Make optional
            "phone": {"required": False},
            "city": {"required": False},
            "avatar": {"required": False},
            "password_confirm": {"required": False},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        if password_confirm and password != password_confirm:  # Only check if provided
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)  # Remove confirm field
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            **{
                k: v
                for k, v in validated_data.items()
                if k not in ["email", "password"]
            }
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"  # Tell JWT to use email instead of username

    def validate(self, attrs):
        # Override to use email for authentication
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password.")
        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_empty_file=True)

    class Meta:
        model = User
        fields = ["name", "phone", "city", "avatar"]

    def validate_avatar(self, value):
        if value:
            # Check file type (similar to frontend)
            allowed_types = [
                "image/png",
                "image/jpeg",
                "image/jpg",
                "image/gif",
                "image/webp",
            ]
            if (
                value.content_type not in allowed_types
                and not value.content_type.startswith("image/")
            ):
                raise serializers.ValidationError(
                    "Только изображения разрешены (PNG, JPEG и т.д.)."
                )
            # Check file size (2MB limit)
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("Файл слишком большой (макс. 2MB).")
        return value
