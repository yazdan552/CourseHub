from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm
from .models import Course, Instructor


# Create your views here.



def course_list(request):
    courses = Course.objects.all()

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
        },
    )

