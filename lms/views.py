from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CourseForm
from .models import Course, Material, Testing, TestResult, Enrollment, User
from .serializers import CourseSerializer, MaterialSerializer, TestingSerializer, TestResultSerializer, \
    EnrollmentSerializer, CourseListSerializer
from .permissions import IsTeacherOrAdmin, IsCourseOwnerOrAdmin, IsStudentOrSubscribed


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/course_form.html'

    def test_func(self):
        """Only teachers can create courses"""
        return self.request.user.role == 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание курса'
        context['form'] = CourseForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            messages.error(request, "Только преподаватели могут создавать курсы")
            return redirect('dashboard')

        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            # Use serializer for validation (diploma requirement)
            from .serializers import CourseSerializer
            serializer = CourseSerializer(data=request.POST, context={'request': request})

            if serializer.is_valid():
                course = form.save(commit=False)
                course.owner = request.user
                course.save()
                messages.success(request, 'Курс успешно создан!')
                return redirect('course-detail', course_id=course.id)
            else:
                # Add serializer errors to form
                for field, errors in serializer.errors.items():
                    for error in errors:
                        form.add_error(field, error)

        return self.render_to_response({
            'form': form,
            'title': 'Создание курса'
        })


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'lms/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        is_teacher = self.request.user.is_authenticated and self.request.user.role == 'teacher'
        is_owner = self.request.user.is_authenticated and course.owner == self.request.user
        is_enrolled = self.request.user.is_authenticated and course.students.filter(id=self.request.user.id).exists()

        materials_count = course.materials.count()
        tests_count = course.materials.filter(test__isnull=False).count()
        materials = course.materials.all()
        tests = Testing.objects.filter(material__course=course).distinct()

        context.update({
            'course': course,
            'materials_count': materials_count,
            'tests_count': tests_count,
            'is_teacher': is_teacher,
            'is_owner': is_owner,
            'is_enrolled': is_enrolled,
            'materials': materials,
            'tests': tests
        })

        # ONLY show teacher tools if user is the actual owner
        if is_owner:
            context['enrollments'] = Enrollment.objects.filter(course=course).select_related('student')
            context['show_teacher_tools'] = True

        # Student enrollment check
        if self.request.user.is_authenticated:
            user_enrolled = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).exists()

            if user_enrolled:
                materials = course.materials.all().prefetch_related('test')
                context.update({
                    'user_enrolled': True,
                    'materials': materials,
                })
            else:
                context.update({
                    'user_enrolled': False,
                })

        # Use serializer for diploma requirements
        from .serializers import CourseSerializer
        serializer = CourseSerializer(course, context={'request': self.request})
        context['serialized_course'] = serializer.data

        return context


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('materials').all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        else:  # update, partial_update, destroy, edit, add_material
            return [permissions.IsAuthenticated(), IsCourseOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Автоматически устанавливаем владельца

    @action(detail=True, methods=['patch'], url_path='edit')
    def edit(self, request, pk=None):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add-material')
    def add_material(self, request, pk=None):
        course = self.get_object()
        if not (request.user.is_superuser or request.user == course.owner):
            return Response(
                {"error": "У вас нет прав добавления материалов в этот курс"},
                status=status.HTTP_403_FORBIDDEN
            )
        # Создаем копию данных и добавляем курс и владельца
        material_data = request.data.copy()
        serializer = MaterialSerializer(data=material_data)

        if serializer.is_valid():
            # Сохраняем материал с привязкой к курсу и текущему пользователю как владельцу
            material = serializer.save(
                course=course,
                owner=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseListView(TemplateView):
    template_name = 'lms/course_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get and filter courses (same logic as before)
        courses = Course.objects.all().prefetch_related('materials', 'owner')

        # Search functionality (same as before)
        search_query = self.request.GET.get('search', '')
        if search_query:
            courses = courses.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Annotate courses (same as before)
        courses = courses.annotate(
            materials_count=Count('materials'),
            tests_count=Count('materials__test')
        )

        # ✅ USE YOUR NEW SERIALIZER
        serializer = CourseListSerializer(courses, many=True, context={'request': self.request})

        # Platform statistics (same as before)
        context.update({
            'courses': courses,  # Keep original QuerySet for template
            'serialized_courses': serializer.data,  # For diploma requirements
            'total_courses': Course.objects.count(),
            'total_materials': Material.objects.count(),
            'total_tests': Testing.objects.count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_enrollments': Enrollment.objects.count(),
            'search_query': search_query,
            'user_is_authenticated': self.request.user.is_authenticated,
        })
        return context


class CourseEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/course_edit.html'

    def test_func(self):
        """Only course owner or admin can edit"""
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Use serializer for data preparation
        serializer = CourseSerializer(course, context={'request': self.request})

        context.update({
            'course': course,
            'form': CourseForm(instance=course),  # Your existing form
            'serialized_course': serializer.data,  # For diploma requirements
            'title': f'Редактирование курса: {course.title}'
        })
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для редактирования этого курса")
            return redirect('course-detail', course_id=course_id)

        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            # Use serializer for validation (diploma requirement)
            serializer = CourseSerializer(
                course,
                data=request.POST,
                context={'request': request},
                partial=True  # Allow partial updates
            )

            if serializer.is_valid():
                form.save()
                messages.success(request, 'Курс успешно обновлен!')
                return redirect('course-detail', course_id=course_id)
            else:
                # Add serializer errors to form
                for field, errors in serializer.errors.items():
                    for error in errors:
                        form.add_error(field, error)

        return self.render_to_response({
            'form': form,
            'course': course,
            'title': f'Редактирование курса: {course.title}'
        })


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/course_confirm_delete.html'

    def test_func(self):
        """Only course owner or admin can delete"""
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        context.update({
            'course': course,
            'title': f'Удаление курса: {course.title}'
        })
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для удаления этого курса")
            return redirect('course-detail', course_id=course_id)

        # Use serializer for diploma requirements (optional validation)
        serializer = CourseSerializer(course, context={'request': request})

        course_title = course.title
        course.delete()

        messages.success(request, f'Курс "{course_title}" успешно удален!')
        return redirect('course_list')


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCourseOwnerOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MaterialDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'lms/material_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs['material_id']
        material = get_object_or_404(
            Material.objects.select_related('course', 'owner'),
            id=material_id
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
        material_serializer = MaterialSerializer(material, context={'request': self.request})
        test_serializer = TestingSerializer(testing, context={'request': self.request}) \
            if testing else None

        context.update({
            'material': material,
            'test': testing,
            'is_owner': is_owner,
            'is_course_owner': is_course_owner,
            'can_edit': can_edit,
            'has_test': testing is not None,
            'serialized_material': material_serializer.data,
            'serialized_test': test_serializer.data if test_serializer else None,
        })
        return context


class MaterialCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/material_form.html'

    def test_func(self):
        """Only course owner or admin can add materials"""
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        return self.request.user == course.owner or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        context.update({
            'course': course,
            'title': f'Добавить материал в курс: {course.title}',
            'errors': {},
            'form_data': {}
        })
        return context

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для добавления материалов в этот курс")
            return redirect('course-detail', course_id=course_id)

        # Validate only non-file fields with serializer
        validation_data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'video_link': request.POST.get('video_link', ''),
        }

        serializer = MaterialSerializer(data=validation_data, context={'request': request})

        if serializer.is_valid():
            # Create material directly
            material = Material(
                title=validation_data['title'],
                content=validation_data['content'],
                video_link=validation_data['video_link'],
                course=course,
                owner=request.user
            )

            # Handle optional file field
            if request.FILES.get('illustration'):
                material.illustration = request.FILES['illustration']

            material.save()

            messages.success(request, 'Материал успешно добавлен!')
            return redirect('course-detail', course_id=course_id)
        else:
            # Return form with errors
            return self.render_to_response({
                'course': course,
                'title': f'Добавить материал в курс: {course.title}',
                'errors': serializer.errors,
                'form_data': request.POST
            })


class MaterialEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/material_form.html'

    def test_func(self):
        """Only material owner or course owner can edit"""
        material_id = self.kwargs['material_id']
        material = get_object_or_404(Material, id=material_id)
        return (self.request.user == material.owner or
                self.request.user == material.course.owner or
                self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs['material_id']
        course_id = self.kwargs['course_id']
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        context.update({
            'course': course,
            'material': material,
            'title': f'Редактирование материала: {material.title}',
            'is_edit': True,
            'form_data': {
                'title': material.title,
                'content': material.content,
                'video_link': material.video_link or '',
            }
        })
        return context

    def post(self, request, *args, **kwargs):
        material_id = self.kwargs['material_id']
        course_id = self.kwargs['course_id']
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == material.owner or request.user == material.course.owner
                or request.user.is_superuser):
            messages.error(request, "У вас нет прав для редактирования этого материала")
            return redirect('material-detail', material_id=material_id)

        # Validate with serializer
        validation_data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'video_link': request.POST.get('video_link', ''),
        }

        serializer = MaterialSerializer(instance=material, data=validation_data,
                                        context={'request': request})

        if serializer.is_valid():
            # Update material
            material.title = validation_data['title']
            material.content = validation_data['content']
            material.video_link = validation_data['video_link']
            # No description field - removed

            # Handle file updates
            if request.FILES.get('illustration'):
                material.illustration = request.FILES['illustration']

            material.save()

            messages.success(request, 'Материал успешно обновлен!')
            return redirect('material-detail', material_id=material_id)
        else:
            # Return form with errors
            return self.render_to_response({
                'course': course,
                'material': material,
                'title': f'Редактирование материала: {material.title}',
                'is_edit': True,
                'errors': serializer.errors,
                'form_data': request.POST
            })


class MaterialDeleteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lms/material_confirm_delete.html'

    def test_func(self):
        """Only material owner or course owner can delete"""
        material_id = self.kwargs['material_id']
        material = get_object_or_404(Material, id=material_id)
        return (self.request.user == material.owner or
                self.request.user == material.course.owner or
                self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material_id = self.kwargs['material_id']
        course_id = self.kwargs['course_id']
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        context.update({
            'course': course,
            'material': material,
            'title': f'Удаление материала'
        })
        return context

    def post(self, request, *args, **kwargs):
        material_id = self.kwargs['material_id']
        course_id = self.kwargs['course_id']
        material = get_object_or_404(Material, id=material_id)
        course = get_object_or_404(Course, id=course_id)

        # Check permission again
        if not (request.user == material.owner or request.user == material.course.owner or request.user.is_superuser):
            messages.error(request, "У вас нет прав для удаления этого материала")
            return redirect('material-detail', material_id=material_id)

        # Delete the material
        material_title = material.title
        material.delete()

        messages.success(request, f'Материал "{material_title}" успешно удален!')
        return redirect('course-detail', course_id=course_id)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Testing.objects.all()
    serializer_class = TestingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated(), IsStudentOrSubscribed()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role

        if role == 'teacher':
            courses = Course.objects.filter(owner=request.user).prefetch_related('materials')
            print("Teacher courses found:", courses.count())
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "teacher", "courses": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            enrollments = Enrollment.objects.filter(user=request.user).select_related('course').prefetch_related(
                'course__materials')
            print("Student enrollments found:", enrollments.count())
            courses = [enrollment.course for enrollment in enrollments]
            print("Student courses found:", len(courses))
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {"role": "student", "courses": serializer.data},
                status=status.HTTP_200_OK
            )


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user,
                course=course
            )
            if created:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {"message": "Успешно записаны на курс!", "enrollment": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            else:
                serializer = EnrollmentSerializer(enrollment)
                return Response(
                    {"message": "Вы уже записаны на этот курс.", "enrollment": serializer.data},
                    status=status.HTTP_200_OK
                )
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND)


class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrSubscribed]

    def post(self, request, test_id):
        try:
            test = Testing.objects.get(id=test_id)
            if not Enrollment.objects.filter(user=request.user, course=test.material.course).exists():
                return Response({"error": "Not enrolled in this course."}, status=403)

            # Простая функция для расчета баллов
            def calculate_score(questions, answers):
                correct = 0
                total = len(questions)
                for i, q in enumerate(questions):
                    if answers.get(str(i)) == q['correct']:
                        correct += 1
                return (correct / total) * 100 if total > 0 else 0

            answers = request.data.get('answers', {})
            score = calculate_score(test.questions, answers)
            passed = score >= 70
            TestResult.objects.create(user=request.user, test=test, answers=answers,
                                      score=score, passed=passed)
            return Response({"score": score, "passed": passed}, status=201)
        except Testing.DoesNotExist:
            return Response({"error": "Test not found."}, status=404)


def dashboard(request):
    # Get statistics
    total_courses = Course.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_students = User.objects.filter(role='student').count()

    context = {
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_students': total_students,
    }

    return render(request, 'dashboard.html', context)


def authors(request):
    """Display all teachers/authors"""
    teachers = User.objects.filter(role='teacher')

    return render(request, 'lms/authors.html', {
        'teachers': teachers
    })


def discussions(request):
    """Discussion forum page"""
    # For now, we'll create a simple placeholder
    # You can expand this with actual discussion functionality later

    return render(request, 'lms/discussions.html')


def author_courses(request, teacher_id):
    """Show courses by a specific author"""
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    courses = Course.objects.filter(owner=teacher)

    return render(request, 'lms/author_courses.html', {
        'teacher': teacher,
        'courses': courses
    })


@login_required
def enroll_course_template(request, course_id):
    """Handle course enrollment via template"""
    course = get_object_or_404(Course, id=course_id)

    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}')

    return redirect('course_detail_template', course_id=course_id)


@login_required
def profile(request):
    """Main profile page - shows different content based on role"""
    user = request.user
    context = {'user': user}

    if user.role == 'student':
        # Use the correct relationship name
        try:
            # Option 1: Use enrolled_courses (ManyToMany through Enrollment)
            if hasattr(user, 'enrolled_courses'):
                context['courses'] = user.enrolled_courses.all()

            # Option 2: Use enrollment_set to get Enrollment objects with progress
            if hasattr(user, 'enrollment_set'):
                context['enrollments'] = user.enrollment_set.all().select_related('course')
            else:
                # Fallback: direct database query
                from lms.models import Enrollment
                context['enrollments'] = Enrollment.objects.filter(student=user).select_related('course')
        except Exception as e:
            print(f"Error getting student data: {e}")
            context['enrollments'] = []

    elif user.role == 'teacher':
        # Use courses_created relationship
        try:
            if hasattr(user, 'courses_created'):
                context['my_courses'] = user.courses_created.all()
            else:
                # Fallback: direct database query
                from lms.models import Course
                context['my_courses'] = Course.objects.filter(owner=user)

            # ✅ ADD STATISTICS CALCULATIONS
            from lms.models import Material, Enrollment

            # Calculate total materials created by this teacher
            total_materials = Material.objects.filter(owner=user).count()

            # Calculate total students across all teacher's courses
            total_students = Enrollment.objects.filter(course__owner=user).count()

            # Add statistics to context
            context['total_materials'] = total_materials
            context['total_students'] = total_students

        except Exception as e:
            print(f"Error getting teacher courses: {e}")
            context['my_courses'] = []
            context['total_materials'] = 0
            context['total_students'] = 0

    return render(request, 'users/profile.html', context)
