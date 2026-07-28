from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm, RegisterForm
from .models import Course, Instructor, Enrollment
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


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


@login_required
def my_courses(request):
    enrollments = request.user.enrollments.select_related("course", )
    return render(
        request,
        "courses/my_courses.html",
        {
            "enrollments": enrollments,
        }
    )


def course_detail(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).exists()

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
        },
    )


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.method == "POST":
        Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
        )

        messages.success(
            request,
            "You enrolled in this course.",
        )

        return redirect(
            "course_detail",
            course.id,
        )

    return redirect(
        "course_detail",
        course.id,
    )


@login_required
def unenroll_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )
    if request.method == "POST":
        Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).delete()

        messages.success(
            request,
            "You left this course.",
        )

        return redirect(
            "course_detail",
            course.id,
        )
    return redirect(
        "course_detail",
        course.id,
    )


@staff_member_required
def create_course(request):
    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():
            course = form.save(
                commit=False,
            )

            course.instructor = request.user.instructor

            course.save()

            messages.success(
                request,
                "Course created successfully.",
            )

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
    if course.instructor != request.user.instructor:
        return HttpResponseForbidden(
            "You are not allowed to edit this course."
        )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Course updated successfully.",
            )

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

    if course.instructor != request.user.instructor:
        return HttpResponseForbidden(
            "You are not allowed to delete this course."
        )

    if request.method == "POST":
        course.delete()

        messages.success(
            request,
            "Course deleted successfully.",
        )

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

            Instructor.objects.create(
                user=user,
                phone="",
                bio="",
            )

            login(request, user)

            messages.success(
                request,
                "Registration completed successfully.",
            )

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
