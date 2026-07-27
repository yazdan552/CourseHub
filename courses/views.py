from django.shortcuts import render, redirect, get_object_or_404
from .forms import  CourseForm, RegisterForm
from .models import Course, Instructor
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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


@staff_member_required
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


@staff_member_required
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



@staff_member_required
def delete_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.method == "POST":

        course.delete()

        return redirect("course_list")

    return render(
        request,
        "courses/course_confirm_delete.html",
        {
            "course": course,
        },
    )






def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("course_list")

    else:

        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        },
    )