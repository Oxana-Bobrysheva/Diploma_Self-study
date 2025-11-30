from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CourseForm, TestingForm
from .models import (
    Course,
    Material,
    Testing,
    Enrollment,
    User,
    Question,
    Answer,
    TestAttempt,
)
from .serializers import (
    CourseSerializer,
    MaterialSerializer,
    TestingSerializer,
    EnrollmentSerializer,
    CourseListSerializer,
    QuestionSerializer,
)
from .permissions import IsTeacherOrAdmin, IsCourseOwnerOrAdmin, IsStudentOrSubscribed


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/course_form.html"

    def test_func(self):
        """Only teachers can create courses"""
        return self.request.user.role == "teacher"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание курса"
        context["form"] = CourseForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.user.role != "teacher":
            messages.error(request, "Только преподаватели могут создавать курсы")
            return redirect("dashboard")

        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            # Use serializer for validation (diploma requirement)
            from .serializers import CourseSerializer

            serializer = CourseSerializer(
                data=request.POST, context={"request": request}
            )

            if serializer.is_valid():
                course = form.save(commit=False)
                course.owner = request.user
                course.save()
                messages.success(request, "Курс успешно создан!")
                return redirect("course-detail", course_id=course.id)
            else:
                # Add serializer errors to form
                for field, errors in serializer.errors.items():
                    for error in errors:
                        form.add_error(field, error)

        return self.render_to_response({"form": form, "title": "Создание курса"})


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = "lms/course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        is_teacher = (
            self.request.user.is_authenticated and self.request.user.role == "teacher"
        )
        is_owner = (
            self.request.user.is_authenticated and course.owner == self.request.user
        )
        is_enrolled = (
            self.request.user.is_authenticated
            and course.students.filter(id=self.request.user.id).exists()
        )

        materials_count = course.materials.count()
        tests_count = course.materials.filter(testing__isnull=False).count()
        materials = course.materials.all()
        tests = Testing.objects.filter(material__course=course).distinct()

        context.update(
            {
                "course": course,
                "materials_count": materials_count,
                "tests_count": tests_count,
                "is_teacher": is_teacher,
                "is_owner": is_owner,
                "is_enrolled": is_enrolled,
                "materials": materials,
                "tests": tests,
            }
        )

        # ONLY show teacher tools if user is the actual owner
        if is_owner:
            context["enrollments"] = Enrollment.objects.filter(
                course=course
            ).select_related("student")
            context["show_teacher_tools"] = True

        # Student enrollment check
        if self.request.user.is_authenticated:
            user_enrolled = Enrollment.objects.filter(
                student=self.request.user, course=course
            ).exists()

            if user_enrolled:
                materials = course.materials.all().prefetch_related("testing")
                context.update(
                    {
                        "user_enrolled": True,
                        "materials": materials,
                    }
                )
            else:
                context.update(
                    {
                        "user_enrolled": False,
                    }
                )

        # Use serializer for diploma requirements
        from .serializers import CourseSerializer

        serializer = CourseSerializer(course, context={"request": self.request})
        context["serialized_course"] = serializer.data

        return context


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related("materials").all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == "list":
            return [permissions.AllowAny()]
        elif self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        else:  # update, partial_update, destroy, edit, add_material
            return [permissions.IsAuthenticated(), IsCourseOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )  # Автоматически устанавливаем владельца

    @action(detail=True, methods=["patch"], url_path="edit")
    def edit(self, request, pk=None):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="add-material")
    def add_material(self, request, pk=None):
        course = self.get_object()
        if not (request.user.is_superuser or request.user == course.owner):
            return Response(
                {"error": "У вас нет прав добавления материалов в этот курс"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Создаем копию данных и добавляем курс и владельца
        material_data = request.data.copy()
        serializer = MaterialSerializer(data=material_data)

        if serializer.is_valid():
            # Сохраняем материал с привязкой к курсу и текущему пользователю как владельцу
            material = serializer.save(course=course, owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseListView(TemplateView):
    template_name = "lms/course_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get and filter courses (same logic as before)
        courses = Course.objects.all().prefetch_related("materials", "owner")

        # Search functionality (same as before)
        search_query = self.request.GET.get("search", "")
        if search_query:
            courses = courses.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # Annotate courses (same as before)
        courses = courses.annotate(
            materials_count=Count("materials"), tests_count=Count("materials__testing")
        )

        # ✅ USE YOUR NEW SERIALIZER
        serializer = CourseListSerializer(
            courses, many=True, context={"request": self.request}
        )

        # Platform statistics (same as before)
        context.update(
            {
                "courses": courses,  # Keep original QuerySet for template
                "serialized_courses": serializer.data,  # For diploma requirements
                "total_courses": Course.objects.count(),
                "total_materials": Material.objects.count(),
                "total_tests": Testing.objects.count(),
                "total_teachers": User.objects.filter(role="teacher").count(),
                "total_enrollments": Enrollment.objects.count(),
                "search_query": search_query,
                "user_is_authenticated": self.request.user.is_authenticated,
            }
        )
        return context


class CourseEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/course_edit.html"

    def test_func(self):
        """Only course owner or admin can edit"""
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        # Use serializer for data preparation
        serializer = CourseSerializer(course, context={"request": self.request})

        context.update(
            {
                "course": course,
                "form": CourseForm(instance=course),  # Your existing form
                "serialized_course": serializer.data,  # For diploma requirements
                "title": f"Редактирование курса: {course.title}",
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для редактирования этого курса")
            return redirect("course-detail", course_id=course_id)

        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            # Use serializer for validation (diploma requirement)
            serializer = CourseSerializer(
                course,
                data=request.POST,
                context={"request": request},
                partial=True,  # Allow partial updates
            )

            if serializer.is_valid():
                form.save()
                messages.success(request, "Курс успешно обновлен!")
                return redirect("course-detail", course_id=course_id)
            else:
                # Add serializer errors to form
                for field, errors in serializer.errors.items():
                    for error in errors:
                        form.add_error(field, error)

        return self.render_to_response(
            {
                "form": form,
                "course": course,
                "title": f"Редактирование курса: {course.title}",
            }
        )


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/course_confirm_delete.html"

    def test_func(self):
        """Only course owner or admin can delete"""
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        context.update({"course": course, "title": f"Удаление курса: {course.title}"})
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для удаления этого курса")
            return redirect("course-detail", course_id=course_id)

        # Use serializer for diploma requirements (optional validation)
        serializer = CourseSerializer(course, context={"request": request})

        course_title = course.title
        course.delete()

        messages.success(request, f'Курс "{course_title}" успешно удален!')
        return redirect("course_list")


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsCourseOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MaterialDetailView(LoginRequiredMixin, TemplateView):
    template_name = "lms/material_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs["material_id"]
        material = get_object_or_404(
            Material.objects.select_related("course", "owner"), id=material_id
        )

        # Check permissions
        is_owner = self.request.user == material.owner or self.request.user.is_superuser
        is_course_owner = self.request.user == material.course.owner
        can_edit = is_owner or is_course_owner

        # Get test if exists
        testing = None
        try:
            test = material.testing
        except Testing.DoesNotExist:
            pass

        # Use serializer for data
        material_serializer = MaterialSerializer(
            material, context={"request": self.request}
        )
        test_serializer = (
            TestingSerializer(testing, context={"request": self.request})
            if testing
            else None
        )

        context.update(
            {
                "material": material,
                "test": testing,
                "is_owner": is_owner,
                "is_course_owner": is_course_owner,
                "can_edit": can_edit,
                "has_test": testing is not None,
                "serialized_material": material_serializer.data,
                "serialized_test": test_serializer.data if test_serializer else None,
            }
        )
        return context


class MaterialCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/material_form.html"

    def test_func(self):
        """Only course owner or admin can add materials"""
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        context.update(
            {
                "course": course,
                "title": f"Добавить материал в курс: {course.title}",
                "errors": {},
                "form_data": {},
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(
                request, "У вас нет прав для добавления материалов в этот курс"
            )
            return redirect("course-detail", course_id=course_id)

        # Validate only non-file fields with serializer
        validation_data = {
            "title": request.POST.get("title"),
            "content": request.POST.get("content"),
            "video_link": request.POST.get("video_link", ""),
        }

        serializer = MaterialSerializer(
            data=validation_data, context={"request": request}
        )

        if serializer.is_valid():
            # Create material directly
            material = Material(
                title=validation_data["title"],
                content=validation_data["content"],
                video_link=validation_data["video_link"],
                course=course,
                owner=request.user,
            )

            # Handle optional file field
            if request.FILES.get("illustration"):
                material.illustration = request.FILES["illustration"]

            material.save()

            messages.success(request, "Материал успешно добавлен!")
            return redirect("course-detail", course_id=course_id)
        else:
            # Return form with errors
            return self.render_to_response(
                {
                    "course": course,
                    "title": f"Добавить материал в курс: {course.title}",
                    "errors": serializer.errors,
                    "form_data": request.POST,
                }
            )


class MaterialEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/material_form.html"

    def test_func(self):
        """Only material owner or course owner can edit"""
        material_id = self.kwargs["material_id"]
        material = get_object_or_404(Material, id=material_id)
        return (
            self.request.user == material.owner
            or self.request.user == material.course.owner
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs["material_id"]
        course_id = self.kwargs["course_id"]
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        context.update(
            {
                "course": course,
                "material": material,
                "title": f"Редактирование материала: {material.title}",
                "is_edit": True,
                "form_data": {
                    "title": material.title,
                    "content": material.content,
                    "video_link": material.video_link or "",
                },
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        material_id = self.kwargs["material_id"]
        course_id = self.kwargs["course_id"]
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (
            request.user == material.owner
            or request.user == material.course.owner
            or request.user.is_superuser
        ):
            messages.error(request, "У вас нет прав для редактирования этого материала")
            return redirect("material-detail", material_id=material_id)

        # Validate with serializer
        validation_data = {
            "title": request.POST.get("title"),
            "content": request.POST.get("content"),
            "video_link": request.POST.get("video_link", ""),
        }

        serializer = MaterialSerializer(
            instance=material, data=validation_data, context={"request": request}
        )

        if serializer.is_valid():
            # Update material
            material.title = validation_data["title"]
            material.content = validation_data["content"]
            material.video_link = validation_data["video_link"]
            # No description field - removed

            # Handle file updates
            if request.FILES.get("illustration"):
                material.illustration = request.FILES["illustration"]

            material.save()

            messages.success(request, "Материал успешно обновлен!")
            return redirect("material-detail", material_id=material_id)
        else:
            # Return form with errors
            return self.render_to_response(
                {
                    "course": course,
                    "material": material,
                    "title": f"Редактирование материала: {material.title}",
                    "is_edit": True,
                    "errors": serializer.errors,
                    "form_data": request.POST,
                }
            )


class MaterialDeleteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/material_confirm_delete.html"

    def test_func(self):
        """Only material owner or course owner can delete"""
        material_id = self.kwargs["material_id"]
        material = get_object_or_404(Material, id=material_id)
        return (
            self.request.user == material.owner
            or self.request.user == material.course.owner
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs["material_id"]
        course_id = self.kwargs["course_id"]
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        context.update(
            {"course": course, "material": material, "title": f"Удаление материала"}
        )
        return context

    def post(self, request, *args, **kwargs):
        material_id = self.kwargs["material_id"]
        course_id = self.kwargs["course_id"]
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (
            request.user == material.owner
            or request.user == material.course.owner
            or request.user.is_superuser
        ):
            messages.error(request, "У вас нет прав для удаления этого материала")
            return redirect("material-detail", material_id=material_id)

        # Delete the material
        material_title = material.title
        material.delete()

        messages.success(request, f'Материал "{material_title}" успешно удален!')
        return redirect("course-detail", course_id=course_id)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Testing.objects.all()
    serializer_class = TestingSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role

        if role == "teacher":
            courses = Course.objects.filter(owner=request.user).prefetch_related(
                "materials"
            )
            print("Teacher courses found:", courses.count())
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "teacher", "courses": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            enrollments = (
                Enrollment.objects.filter(student=request.user)
                .select_related("course")
                .prefetch_related("course__materials")
            )
            print("Student enrollments found:", enrollments.count())
            courses = [enrollment.course for enrollment in enrollments]
            print("Student courses found:", len(courses))
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "student", "courses": serializer.data},
                status=status.HTTP_200_OK,
            )


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.student, course=course
            )
            if created:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {
                        "message": "Успешно записаны на курс!",
                        "enrollment": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {
                        "message": "Вы уже записаны на этот курс.",
                        "enrollment": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND
            )


class TestingCreateView(CreateView):
    model = Testing
    form_class = TestingForm
    template_name = "lms/testing_create.html"


    def dispatch(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404
        from lms.models import Material

        self.material_id = self.kwargs["material_id"]
        self.material = get_object_or_404(Material.objects.select_related('course'), id=self.material_id)
        print(f"DEBUG: Material loaded - {self.material.title}")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['material_id'] = self.material_id
        context['course_id'] = self.material.course.id
        context['material'] = self.material

        from lms.models import Question
        context['question_types'] = Question.QUESTION_TYPES
        return context

    def get_success_url(self):
        from django.urls import reverse
        return reverse('material-detail', kwargs={'material_id': self.material_id})

    def form_valid(self, form):
        print("DEBUG: Form is valid")
        print(f"DEBUG: Form data - {form.cleaned_data}")

        form.instance.material_id = self.material_id
        form.instance.owner = self.request.user

        # Save the testing object
        response = super().form_valid(form)
        testing = self.object
        print(f"DEBUG: Testing object created with ID: {testing.id}")

        # Process questions and answers
        self.process_questions(testing)

        print("DEBUG: Redirecting to success URL")
        return response

    def form_invalid(self, form):
        print("DEBUG: Form is INVALID")
        print(f"DEBUG: Form errors: {form.errors}")
        print(f"DEBUG: POST data: {self.request.POST}")
        return super().form_invalid(form)

    def process_questions(self, testing):
        question_count = int(self.request.POST.get("question_count", 0))
        print(f"DEBUG: Processing {question_count} questions")

        for i in range(1, question_count + 1):
            question_key = f"question_{i}"
            question_text = self.request.POST.get(f"{question_key}_text")
            print(f"DEBUG: Question {i} text: {question_text}")

            if question_text:
                question = Question.objects.create(
                    testing=testing,
                    question_type=self.request.POST.get(f"{question_key}_type", "text"),
                    text=question_text,
                    order=i,
                )
                print(f"DEBUG: Created question {i}")

                # Handle file uploads
                if f"{question_key}_image" in self.request.FILES:
                    question.image = self.request.FILES[f"{question_key}_image"]
                    print(f"DEBUG: Added image to question {i}")

                if f"{question_key}_audio" in self.request.FILES:
                    question.audio = self.request.FILES[f"{question_key}_audio"]
                    print(f"DEBUG: Added audio to question {i}")

                question.save()
                self.process_answers(question, i)

    def process_answers(self, question, question_index):
        answer_count = int(self.request.POST.get(f"question_{question_index}_answer_count", 0))
        print(f"DEBUG: Processing {answer_count} answers for question {question_index}")

        for j in range(answer_count):
            answer_text = self.request.POST.get(f"question_{question_index}_answer_{j}_text")
            is_correct = self.request.POST.get(f"question_{question_index}_answer_{j}_correct") == "on"
            print(f"DEBUG: Answer {j} - text: {answer_text}, correct: {is_correct}")

            if answer_text:
                Answer.objects.create(
                    question=question, text=answer_text, is_correct=is_correct, order=j
                )

class TestingDetailView(LoginRequiredMixin, TemplateView):
    template_name = "lms/testing_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testing_id = self.kwargs["testing_id"]
        testing = get_object_or_404(
            Testing.objects.select_related(
                "material", "material__course", "owner"
            ).prefetch_related("questions__answers"),
            id=testing_id,
        )

        # Check permissions
        is_owner = self.request.user == testing.owner or self.request.user.is_superuser
        is_course_owner = self.request.user == testing.material.course.owner
        can_edit = is_owner or is_course_owner

        # Use serializer for data
        serializer = TestingSerializer(testing, context={"request": self.request})

        context.update(
            {
                "testing": testing,
                "is_owner": is_owner,
                "is_course_owner": is_course_owner,
                "can_edit": can_edit,
                "serialized_testing": serializer.data,
                "title": f"Тест: {testing.title}",
            }
        )
        return context


class TestingUpdateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "lms/testing_update.html"

    def test_func(self):
        """Only test owner or course owner can edit"""
        testing_id = self.kwargs["testing_id"]
        testing = get_object_or_404(Testing, id=testing_id)
        return (
            self.request.user == testing.owner
            or self.request.user == testing.material.course.owner
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testing_id = self.kwargs["testing_id"]
        testing = get_object_or_404(
            Testing.objects.select_related("material").prefetch_related(
                "questions__answers"
            ),
            id=testing_id,
        )

        context.update(
            {
                "testing": testing,
                "question_types": Question.QUESTION_TYPES,
                "title": f"Редактирование теста: {testing.title}",
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        testing_id = self.kwargs["testing_id"]
        testing = get_object_or_404(Testing, id=testing_id)

        # Check permission
        if not (
            request.user == testing.owner
            or request.user == testing.material.course.owner
            or request.user.is_superuser
        ):
            messages.error(request, "У вас нет прав для редактирования этого теста")
            return redirect("testing-detail", testing_id=testing_id)

        try:
            # Update test basic info
            testing.title = request.POST.get("test_title", testing.title)
            testing.description = request.POST.get(
                "test_description", testing.description
            )
            testing.time_limit = int(request.POST.get("time_limit", testing.time_limit))
            testing.passing_score = int(
                request.POST.get("passing_score", testing.passing_score)
            )
            testing.save()

            # For now, we'll just update existing questions
            # Later we can add full question management

            messages.success(request, "Тест успешно обновлен!")
            return redirect("testing-detail", testing_id=testing_id)

        except Exception as e:
            messages.error(request, f"Ошибка при обновлении теста: {str(e)}")
            return self.render_to_response(self.get_context_data())


class QuestionCreateView(CreateView):
    model = Question
    template_name = "lms/question_form.html"
    fields = ["question_type", "text", "image", "audio", "order"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testing_id"] = self.kwargs["testing_id"]
        return context

    def form_valid(self, form):
        # Save the question first
        form.instance.testing_id = self.kwargs["testing_id"]
        self.object = form.save()

        # Handle answers
        answers = self.request.POST.getlist("answers[]")
        correct_answer_index = int(self.request.POST.get("correct_answer", 0))

        for i, answer_text in enumerate(answers):
            if answer_text.strip():  # Only save non-empty answers
                Answer.objects.create(
                    question=self.object,
                    text=answer_text.strip(),
                    is_correct=(i == correct_answer_index),
                    order=i,
                )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "testing-detail", kwargs={"testing_id": self.kwargs["testing_id"]}
        )


class QuestionUpdateView(UpdateView):
    model = Question
    template_name = "lms/question_form.html"
    fields = ["question_type", "text", "image", "audio", "order"]

    def get_success_url(self):
        return reverse_lazy(
            "testing-detail", kwargs={"testing_id": self.object.testing.id}
        )


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return reverse_lazy("testing-detail", kwargs={"pk": self.object.testing.id})


def dashboard(request):
    # Get statistics
    total_courses = Course.objects.count()
    total_teachers = User.objects.filter(role="teacher").count()
    total_students = User.objects.filter(role="student").count()

    context = {
        "total_courses": total_courses,
        "total_teachers": total_teachers,
        "total_students": total_students,
    }

    return render(request, "dashboard.html", context)


def authors(request):
    """Display all teachers/authors"""
    teachers = User.objects.filter(role="teacher")

    return render(request, "lms/authors.html", {"teachers": teachers})


def discussions(request):
    """Discussion forum page"""
    # For now, we'll create a simple placeholder
    # You can expand this with actual discussion functionality later

    return render(request, "lms/discussions.html")


def author_courses(request, teacher_id):
    """Show courses by a specific author"""
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    courses = Course.objects.filter(owner=teacher)

    return render(
        request, "lms/author_courses.html", {"teacher": teacher, "courses": courses}
    )


@login_required
def enroll_course_template(request, course_id):
    """Handle course enrollment via template"""
    course = get_object_or_404(Course, id=course_id)

    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )

    if created:
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}")

    return redirect("course-detail", course_id=course_id)


@login_required
def profile(request):
    """Main profile page - shows different content based on role"""
    user = request.user
    context = {"user": user}

    if user.role == "student":
        # Use the correct relationship name
        try:
            # Option 1: Use enrolled_courses (ManyToMany through Enrollment)
            if hasattr(user, "enrolled_courses"):
                context["courses"] = user.enrolled_courses.all()

            # Option 2: Use enrollment_set to get Enrollment objects with progress
            if hasattr(user, "enrollment_set"):
                context["enrollments"] = user.enrollment_set.all().select_related(
                    "course"
                )
            else:
                # Fallback: direct database query
                from lms.models import Enrollment

                context["enrollments"] = Enrollment.objects.filter(
                    student=user
                ).select_related("course")
        except Exception as e:
            print(f"Error getting student data: {e}")
            context["enrollments"] = []

    elif user.role == "teacher":
        # Use courses_created relationship
        try:
            if hasattr(user, "courses_created"):
                context["my_courses"] = user.courses_created.all()
            else:
                # Fallback: direct database query
                from lms.models import Course

                context["my_courses"] = Course.objects.filter(owner=user)

            # ✅ ADD STATISTICS CALCULATIONS
            from lms.models import Material, Enrollment

            # Calculate total materials created by this teacher
            total_materials = Material.objects.filter(owner=user).count()

            # Calculate total students across all teacher's courses
            total_students = Enrollment.objects.filter(course__owner=user).count()

            # Add statistics to context
            context["total_materials"] = total_materials
            context["total_students"] = total_students

        except Exception as e:
            print(f"Error getting teacher courses: {e}")
            context["my_courses"] = []
            context["total_materials"] = 0
            context["total_students"] = 0

    return render(request, "users/profile.html", context)


class TestTakeView(DetailView):
    model = Testing
    template_name = "lms/test_take.html"
    context_object_name = "testing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["questions"] = self.object.questions.all().prefetch_related("answers")
        return context


class TestSubmitView(View):
    def post(self, request, pk):
        testing = get_object_or_404(Testing, pk=pk)
        questions = testing.questions.all()
        total_questions = questions.count()
        correct_answers = 0

        # Calculate score
        for question in questions:
            submitted_answer_id = request.POST.get(f"question_{question.id}")
            if submitted_answer_id:
                try:
                    correct_answer = question.answers.filter(is_correct=True).first()
                    if correct_answer and int(submitted_answer_id) == correct_answer.id:
                        correct_answers += 1
                except (ValueError, Answer.DoesNotExist):
                    pass

        # Calculate percentage
        score_percentage = (
            (correct_answers / total_questions * 100) if total_questions > 0 else 0
        )
        passed = score_percentage >= testing.passing_score

        # Save test attempt
        test_attempt = TestAttempt.objects.create(
            user=request.user,
            testing=testing,
            score=score_percentage,
            passed=passed,
            total_questions=total_questions,
            correct_answers=correct_answers,
        )

        return redirect("test_result", attempt_id=test_attempt.id)


class TestResultView(DetailView):
    model = TestAttempt
    template_name = "lms/test_result.html"
    context_object_name = "attempt"
    pk_url_kwarg = "attempt_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testing"] = self.object.testing
        return context


class TestingViewSet(viewsets.ModelViewSet):
    queryset = Testing.objects.all()
    serializer_class = TestingSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer  # You'll need to create this
    permission_classes = [permissions.IsAuthenticated]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
