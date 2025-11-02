from django.contrib import admin
from .models import Course, Material, Test, TestResult

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'owner', 'created_at')  # Columns shown in the list view
    search_fields = ('title', 'description')  # Searchable fields
    list_filter = ('owner', 'created_at')  # Filters on the right sidebar
    readonly_fields = ('created_at', 'updated_at')  # Prevent editing timestamps
    ordering = ('-created_at',)  # Sort by newest first

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'owner', 'created_at')  # Includes course for context
    search_fields = ('title', 'content')  # Search in title/content
    list_filter = ('course', 'owner', 'created_at')  # Filter by course/owner
    readonly_fields = ('created_at',)  # Prevent editing created_at
    ordering = ('course', 'id')  # Group by course, then ID

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'material', 'owner', 'created_at')  # Shows linked material
    search_fields = ('material__title',)  # Search via material title (uses related field lookup)
    list_filter = ('owner', 'created_at')  # Filter by owner/date
    readonly_fields = ('created_at',)  # Prevent editing created_at
    ordering = ('-created_at',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'score', 'passed', 'completed_at')  # Key result info
    search_fields = ('user__username', 'test__material__title')  # Search by user or material
    list_filter = ('passed', 'completed_at')  # Filter by pass status/date
    readonly_fields = ('completed_at',)  # Prevent editing completed_at
    ordering = ('-completed_at',)
