from django.contrib import admin
from .models import Course, Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "price",
        "students_count",
    )