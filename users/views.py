from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, ProfileUpdateForm
from rest_framework.decorators import api_view
from rest_framework.response import Response

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print("Form is valid:", form.is_valid())
        print("Form errors:", form.errors)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('dashboard')  # Redirect to profile page
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """Main profile page - shows different content based on role"""
    user = request.user
    context = {'user': user}

    if user.role == 'student':

        context['enrolled_courses'] = user.enrolled_courses.all()
        context['enrollments'] = user.enrollment_set.all().select_related('course')

    elif user.role == 'teacher':
        context['my_courses'] = user.courses_created.all()

    return render(request, 'users/profile.html', context)

@login_required
def profile_update(request):
    """Update profile information"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'users/profile_update.html', {'form': form})


@api_view(['GET'])
def teachers_list_api(request):
    """API endpoint for teachers list (if needed for AJAX)"""
    teachers = User.objects.filter(role='teacher')
    data = [{'id': t.id, 'name': t.name, 'avatar': t.avatar.url if t.avatar else None}
            for t in teachers]
    return Response(data)