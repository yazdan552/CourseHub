from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


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


# ================ NEW: Category Model ================
class Category(models.Model):
    """
    مدل دسته‌بندی برای سازماندهی دوره‌ها
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Enter the category name (e.g., Python, Web Development)"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name (auto-generated)"
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the category"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']  # مرتب‌سازی بر اساس نام

    def save(self, *args, **kwargs):
        """
        override کردن متد save برای ساخت خودکار slug
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_course_count(self):
        """
        تعداد دوره‌های این دسته‌بندی
        """
        return self.courses.count()



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

    categories = models.ManyToManyField(
        Category,
        related_name="courses",
        blank=True,
        help_text="Select categories for this course"
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