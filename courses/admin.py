from django.contrib import admin
from .models import Course , Instructor
# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','instructor','price','student_count')

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name','email','phone')
