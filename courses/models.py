from django.db import models


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    bio = models.TextField()

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=150)
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    description = models.TextField()
    price = models.PositiveIntegerField()
    students_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title