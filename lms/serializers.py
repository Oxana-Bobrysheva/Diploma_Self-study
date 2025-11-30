from rest_framework import serializers
from .models import Course, Material, Testing, Enrollment, Answer, Question


class MaterialSerializer(serializers.ModelSerializer):
    illustration = serializers.FileField(
        required=False, allow_null=True
    )  # ← ADD required=False
    additional_files = serializers.FileField(
        required=False, allow_null=True
    )  # ← If you have this field

    class Meta:
        model = Material
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "user", "course", "enrolled_at"]
        read_only_fields = ["user", "enrolled_at"]


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list page - extends your existing CourseSerializer"""

    materials_count = serializers.SerializerMethodField()
    tests_count = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "preview",
            "price",
            "owner_name",
            "materials_count",
            "tests_count",
            "created_at",
        ]

    def get_materials_count(self, obj):
        return obj.materials.count()

    def get_tests_count(self, obj):
        return obj.materials.filter(testing__isnull=False).count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail page - extends your existing CourseSerializer"""

    materials = MaterialSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    tests_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"
        # Or specify exact fields if you prefer

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return (
            request.user == obj.owner
            if request and request.user.is_authenticated
            else False
        )

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.students.filter(id=request.user.id).exists()
        return False

    def get_materials_count(self, obj):
        return obj.materials.count()

    def get_tests_count(self, obj):
        return obj.materials.filter(test__isnull=False).count()


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_type", "text", "image", "audio", "order", "answers"]


class TestingSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Testing
        fields = [
            "id",
            "title",
            "description",
            "material",
            "owner",
            "time_limit",
            "passing_score",
            "questions",
            "created_at",
        ]
