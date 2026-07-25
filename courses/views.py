from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm
from .models import Course, Instructor


# Create your views here.


def course_list(request):
    courses = Course.objects.all()
    return render(request,'courses/course_list.html',{'courses':courses})

def course_detail(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    return render(request,'courses/course_detail.html',{'course':course})

def instructor_detail(request,instructor_id):
    instructor = get_object_or_404(Instructor,id=instructor_id)

    return render(request,'courses/instructor_detail.html',{'instructor':instructor})


