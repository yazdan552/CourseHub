from django.contrib import admin
from .models import Course, Instructor, Enrollment, Category


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "price",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "categories",
    )

    search_fields = (
        "title",
        "description",
    )

    filter_horizontal = ("categories",)  # ویجت بهتر برای ManyToMany


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
        "is_completed",
    )

    list_filter = (
        "course",
        "is_completed",
    )

    search_fields = (
        "user__username",
        "course__title",
    )



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "get_course_count",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {"slug": ("name",)}


    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "description")
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )
