from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm, RegisterForm
from .models import Course, Instructor, Enrollment
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


# Create your views here.


def course_list(request):
    """
    نمایش لیست تمام دوره‌ها با شمارش تعداد دانشجویان
    استفاده از annotate برای بهینه‌سازی Query
    """
    courses = Course.objects.select_related('instructor').annotate(
        students_count=Count('enrollments')
    ).filter(is_active=True)  # فقط دوره‌های فعال رو نمایش بده

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
        },
    )


@login_required
def my_courses(request):
    """
    نمایش دوره‌هایی که کاربر در آنها ثبت‌نام کرده
    تفکیک دوره‌های در حال پیشرفت و تکمیل شده
    """
    # دوره‌های در حال پیشرفت
    enrollments = request.user.enrollments.select_related(
        'course__instructor'
    ).filter(
        is_completed=False
    )

    # دوره‌های تکمیل شده
    completed_courses = request.user.enrollments.select_related(
        'course__instructor'
    ).filter(
        is_completed=True
    )

    return render(
        request,
        "courses/my_courses.html",
        {
            "enrollments": enrollments,
            "completed_courses": completed_courses,
        }
    )


def course_detail(request, course_id):
    """
    نمایش جزئیات یک دوره
    بررسی اینکه کاربر قبلاً ثبت‌نام کرده یا نه
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related('enrollments'),
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
    """
    ثبت‌نام کاربر در دوره با بررسی موارد امنیتی:
    1. دوره باید فعال باشد
    2. کاربر نباید مدرس دوره باشد
    3. ظرفیت دوره تکمیل نشده باشد
    4. کاربر قبلاً ثبت‌نام نکرده باشد
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor'),
        id=course_id,
    )

    # بررسی اینکه دوره فعال باشد
    if not course.is_active:
        messages.error(
            request,
            "This course is currently inactive and cannot be enrolled."
        )
        return redirect("course_detail", course.id)

    # جلوگیری از ثبت‌نام مدرس در دوره خودش
    if request.user == course.instructor.user:
        messages.error(
            request,
            "You cannot enroll in your own course."
        )
        return redirect("course_detail", course.id)

    # بررسی ظرفیت دوره
    if course.capacity > 0:
        current_enrollments = course.enrollments.count()
        if current_enrollments >= course.capacity:
            messages.error(
                request,
                "This course is full. No more enrollments accepted."
            )
            return redirect("course_detail", course.id)

    if request.method == "POST":
        # بررسی اینکه کاربر قبلاً ثبت‌نام کرده است
        if Enrollment.objects.filter(
                user=request.user,
                course=course,
        ).exists():
            messages.warning(
                request,
                "You are already enrolled in this course."
            )
        else:
            Enrollment.objects.create(
                user=request.user,
                course=course,
            )
            messages.success(
                request,
                f"You successfully enrolled in {course.title}."
            )

        return redirect("course_detail", course.id)

    return redirect("course_detail", course.id)


@login_required
def unenroll_course(request, course_id):
    """
    لغو ثبت‌نام کاربر از دوره
    """
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
            "You have unenrolled from this course."
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
    """
    ایجاد دوره جدید توسط مدرس
    """
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
    """
    ویرایش دوره (فقط مدرس دوره)
    """
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
    """
    حذف دوره (فقط مدرس دوره)
    """
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
    """
    ثبت‌نام کاربر جدید و ایجاد خودکار Instructor
    """
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