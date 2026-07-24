from django.db import models

# Create your models here.


class Course(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    student_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

