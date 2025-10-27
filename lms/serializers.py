from rest_framework import serializers
from .models import Course, Material, Test, TestResult, Enrollment


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):

    def validate_questions(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Questions must be a list.")
        for q in value:
            if not all(k in q for k in ["question", "answers", "correct"]):
                raise serializers.ValidationError("Each question must have 'question', 'answers', and 'correct'.")
        return value

    class Meta:
        model = Test
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'enrolled_at']
        read_only_fields = ['user', 'enrolled_at']
