from django.contrib.auth.models import User
from django.db import models


class Instructor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="instructor",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )
    bio = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.user.username


class Course(models.Model):
    title = models.CharField(
        max_length=150,
    )

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name="courses",
    )

    description = models.TextField()

    price = models.PositiveIntegerField()

    # فیلدهای جدید اضافه شده
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether the course is available for enrollment."
    )

    capacity = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of students allowed (0 = unlimited)."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True,
    )

    # فیلدهای جدید برای پیگیری پیشرفت
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_completed = models.BooleanField(
        default=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "course",
                ],
                name="unique_user_course_enrollment",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"