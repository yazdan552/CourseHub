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

def course_detail(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
        },
    )


def create_course(request):

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("course_list")

    else:
        form = CourseForm()

    return render(
        request,
        "courses/course_form.html",
        {
            "form": form,
        },
    )

def update_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "course_detail",
                course.id,
            )

    else:

        form = CourseForm(
            instance=course,
        )

    return render(
        request,
        "courses/course_form.html",
        {
            "form": form,
        },
    )