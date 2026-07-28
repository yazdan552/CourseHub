from django.contrib import admin

from .models import Course, Instructor, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "price",
    )


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
    )



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "enrolled_at",
    )

    list_filter = (
        "course",
    )

    search_fields = (
        "user__username",
        "course__title",
    )